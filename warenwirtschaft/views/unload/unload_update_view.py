# warenwirtschaft/views/unload_update_view.py
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
    """
    🇩🇪 Wie RecyclingUpdateView:
    - Checkboxen "selected_unload" steuern die M2M-Verknüpfung (DeliveryUnit ↔ Unload).
    - Aktive Wagen werden als einzelne ModelForms (nicht als FormSet) gerendert.
    - Neue Wagen kommen über UnloadFormSet und werden nach dem Speichern verknüpft.
    - Geänderte Felder bei bestehenden Wagen (status/weight) werden übernommen.
    """
    template_name = "unload/unload_update.html"
    OPEN_STATUS = 1

    # ---------- GET ----------
    def get(self, request, delivery_unit_pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

        #Nur NEUE Wagen im FormSet (wie beim Recycling-Vorbild)
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")

        #Vorhandene aktive Wagen als einzelne Forms + Auswahlmarkierung
        vorhandene_forms = self.build_vorhandene_forms(delivery_unit)

        return self.render_page(formset, vorhandene_forms, delivery_unit)

    # ---------- POST ----------
    def post(self, request, delivery_unit_pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")
        vorhandene_forms = self.build_vorhandene_forms(delivery_unit, data=request.POST)

        #Ausgewählte Wagen-IDs (Checkboxen)
        selected_ids = set(request.POST.getlist("selected_unload"))

        #Validierung: neue + geänderte bestehende
        valid_new = formset.is_valid()
        changed_existing = [f for f, _ in vorhandene_forms if f.has_changed()]
        valid_existing = all(f.is_valid() for f in changed_existing)

        if not (valid_new and valid_existing):
            messages.error(request, "⚠️ Bitte Eingaben prüfen.")
            return self.render_page(formset, vorhandene_forms, delivery_unit)

        with transaction.atomic():
            # 1) Bestehende (nur geänderte) speichern
            for f in changed_existing:
                f.save()

            # 2) M2M gemäß Checkboxen setzen (alle aktiven Wagen)
            for obj in Unload.objects.filter(status=self.OPEN_STATUS):
                if str(obj.pk) in selected_ids:
                    obj.delivery_units.add(delivery_unit)
                else:
                    obj.delivery_units.remove(delivery_unit)

            # 3) Neue Zeilen speichern + verknüpfen
            new_instances = formset.save(commit=False)
            for instance in new_instances:
                if not instance.status:
                    instance.status = self.OPEN_STATUS
                if not getattr(instance, "barcode", None):
                    instance.barcode = self._gen_barcode()
                instance.save()
                instance.delivery_units.add(delivery_unit)
                self._generate_barcode_image(instance)

            # 4) Vom FormSet als gelöscht markierte wirklich löschen (optional)
            for deleted in formset.deleted_objects:
                deleted.delete()

        messages.success(request, "✅ Die Daten sind gespeichert.")
        return redirect(self._success_url(delivery_unit.pk))

    # ---------- Hilfsfunktionen ----------
    def build_vorhandene_forms(self, delivery_unit: DeliveryUnit, data=None):
        """
        🇩🇪 Baut Einzel-ModelForms für alle aktiven Wagen (wie beim Recycling-Vorbild).
        Prefix je Wagen: 'exist_<pk>'.
        """
        ExistingEditForm = ExistingEditFormSet.form  # ModelForm-Klasse aus dem FormSet
        selected_ids = set(
            Unload.objects.filter(delivery_units=delivery_unit).values_list("pk", flat=True)
        )
        forms = []
        for obj in Unload.objects.filter(status=self.OPEN_STATUS).order_by("pk"):
            form = ExistingEditForm(
                data=data if data is not None else None,
                instance=obj,
                prefix=f"exist_{obj.pk}",
            )
            forms.append((form, obj.pk in selected_ids))
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
