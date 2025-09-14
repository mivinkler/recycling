from __future__ import annotations

import uuid
from typing import Iterable

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.contrib import messages

from warenwirtschaft.forms.unload_form import UnloadFormSet, ExistingEditFormSet
from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.services.barcode_service import BarcodeGenerator



class UnloadUpdateView(View):
    template_name = "unload/unload_update.html"
    OPEN_STATUS = 1

    def get(self, request, delivery_unit_pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")

        vorhandene_forms = self.build_vorhandene_forms(delivery_unit)
        return self.render_page(formset, vorhandene_forms, delivery_unit)

    def post(self, request, delivery_unit_pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)
        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")

        # 🇩🇪 Bestehende Wagen: binden mit POST; Initial nur für GET verwendet
        vorhandene_forms = self.build_vorhandene_forms(delivery_unit, data=request.POST)

        # 🇩🇪 Validierung: neue + geänderte bestehende
        valid_new = formset.is_valid()
        # Wir validieren ALLE bestehenden (wegen cleaned_data['selected'])
        valid_existing = all(f.is_valid() for f, _ in vorhandene_forms)

        if not (valid_new and valid_existing):
            messages.error(request, "⚠️ Bitte Eingaben prüfen.")
            return self.render_page(formset, vorhandene_forms, delivery_unit)

        # 🇩🇪 Aus der validierten Form das Auswahl-Set bestimmen
        selected_ids = {
            str(f.instance.pk)
            for f, _ in vorhandene_forms
            if f.cleaned_data.get("selected")
        }

        # 🇩🇪 Nur geänderte bestehende speichern
        changed_existing = [f for f, _ in vorhandene_forms if f.has_changed()]

        with transaction.atomic():
            for f in changed_existing:
                f.save()

            # 🇩🇪 M2M-Verknüpfung gemäß Auswahl setzen
            for obj in Unload.objects.filter(status=self.OPEN_STATUS):
                if str(obj.pk) in selected_ids:
                    obj.delivery_units.add(delivery_unit)
                else:
                    obj.delivery_units.remove(delivery_unit)

            # 🇩🇪 Neue Zeilen speichern + verknüpfen
            new_instances = formset.save(commit=False)
            for instance in new_instances:
                if not instance.status:
                    instance.status = self.OPEN_STATUS
                if not getattr(instance, "barcode", None):
                    instance.barcode = self._gen_barcode()
                instance.save()
                instance.delivery_units.add(delivery_unit)
                self._generate_barcode_image(instance)

            for deleted in formset.deleted_objects:
                deleted.delete()

        messages.success(request, "✅ Die Daten sind gespeichert.")
        return redirect(self._success_url(delivery_unit.pk))

    def build_vorhandene_forms(self, delivery_unit: DeliveryUnit, data=None):
        """
        🇩🇪 Baut Einzel-ModelForms für alle aktiven Wagen.
        - GET: Initial für 'selected' aus der DB-Beziehung.
        - POST: 'data' überschreibt initial automatisch (Django-Mechanik).
        """
        ExistingEditForm = ExistingEditFormSet.form
        selected_ids_db = set(
            Unload.objects.filter(delivery_units=delivery_unit)
                          .values_list("pk", flat=True)
        )

        forms = []
        for obj in Unload.objects.filter(status=self.OPEN_STATUS).order_by("pk"):
            form = ExistingEditForm(
                data=data if data is not None else None,
                instance=obj,
                prefix=f"exist_{obj.pk}",
                selected_initial=(obj.pk in selected_ids_db),
            )
            # 🇩🇪 Für das Template zusätzlich ein bool, wie die Form es gerade sieht
            current_selected = bool(form["selected"].value())
            forms.append((form, current_selected))
        return forms


    def render_page(self, formset, vorhandene_forms, delivery_unit):
        return render(self.request, self.template_name, {
            "delivery_unit": delivery_unit,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_forms": vorhandene_forms,
            "selected_menu": "unload_update",
        })

    @staticmethod
    def _gen_barcode() -> str:
        #Einfaches Barcode-Muster U<8HEX>
        return f"U{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def _generate_barcode_image(unload: Unload) -> None:
        #Fehler beim Bild sollen den Vorgang nicht stoppen
        code = getattr(unload, "barcode", None)
        if not code:
            return
        try:
            BarcodeGenerator(unload, code, "barcodes/unload").generate_image()
        except Exception:
            pass

    def _success_url(self, delivery_unit_pk: int) -> str:
        #Zurück auf dieselbe Update-Seite
        return reverse("unload_update", kwargs={"delivery_unit_pk": delivery_unit_pk})
