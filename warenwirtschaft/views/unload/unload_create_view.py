from __future__ import annotations

import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.forms.unload_form import DeliveryUnitForm, ExistingEditFormSet, UnloadFormSet
from warenwirtschaft.models import Unload
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = "unload/unload_create.html"

    def get(self, request):
        # 🇩🇪 Kopf-Form + leeres FormSet für neue Unloads
        form = DeliveryUnitForm()
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")

        # 🇩🇪 Aktive Wagen (vorhandene Unloads) + FormSet für deren Edit
        vorhandene_unloads = Unload.objects.filter(status=1).order_by("pk")
        existing_formset = ExistingEditFormSet(
            queryset=vorhandene_unloads, prefix="exist"
        )

        return self.render_page(form, formset, vorhandene_unloads, existing_formset)

    def post(self, request):
        delivery_form = DeliveryUnitForm(request.POST)
        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")

        # 🇩🇪 Für bestehende Zeilen den Edit-FormSet binden
        vorhandene_unloads_qs = Unload.objects.filter(status=1).order_by("pk")
        existing_formset = ExistingEditFormSet(
            request.POST, queryset=vorhandene_unloads_qs, prefix="exist"
        )

        selected_ids = request.POST.getlist("selected_unload")

        if delivery_form.is_valid():
            delivery_unit = delivery_form.cleaned_data["delivery_unit"]

            has_new_rows = formset.total_form_count() > 0
            # 🇩🇪 Validierung nur dort, wo es Eingaben gibt
            if has_new_rows and not formset.is_valid():
                return self.render_page(delivery_form, formset, vorhandene_unloads_qs, existing_formset)

            if not existing_formset.is_valid():
                # 🇩🇪 Fehler in bestehenden Zeilen anzeigen
                return self.render_page(delivery_form, formset, vorhandene_unloads_qs, existing_formset)

            with transaction.atomic():
                # 1) 🇩🇪 Bestehende Unloads mit Liefereinheit VERKNÜPFEN (nur hinzufügen)
                if selected_ids:
                    selected_pks = []
                    for pk in selected_ids:
                        try:
                            selected_pks.append(int(pk))
                        except (TypeError, ValueError):
                            pass
                    for unload in Unload.objects.filter(status=1, pk__in=selected_pks):
                        unload.delivery_units.add(delivery_unit)  # idempotent

                # 2) 🇩🇪 Bestehende Unloads (Status/Gewicht) speichern
                #     Nur die beiden Felder sind im Form; M2M bleibt unberührt.
                existing_formset.save()

                # 3) 🇩🇪 Neue Unloads speichern + mit Liefereinheit verknüpfen
                if has_new_rows:
                    new_instances = formset.save(commit=False)
                    for instance in new_instances:
                        if not instance.status:
                            instance.status = 1
                        if not getattr(instance, "barcode", None):
                            instance.barcode = self._gen_barcode()
                        instance.save()
                        instance.delivery_units.add(delivery_unit)
                        self._generate_barcode_image(instance)

            return redirect(reverse("unload_update", kwargs={"pk": delivery_unit.pk}))

        # 🇩🇪 Ungültige Liefereinheit -> Seite neu anzeigen
        vorhandene_unloads = Unload.objects.filter(status=1).order_by("pk")
        return self.render_page(delivery_form, formset, vorhandene_unloads, existing_formset)

    # ---------- Hilfsmethoden ----------

    def render_page(self, form, formset, vorhandene_unloads, existing_formset):
        # 🇩🇪 Zentrales Rendering – jetzt inkl. existing_formset
        return render(self.request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_unloads": vorhandene_unloads,  # für Anzeige (Material/Behälter)
            "existing_formset": existing_formset,      # für Status/Gewicht-Inputs
            "selected_menu": "unload_create",
        })
    
    @staticmethod
    def _gen_barcode() -> str:
        # 🇩🇪 Einfaches Muster „U<8HEX>“
        return f"U{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def _generate_barcode_image(unload: Unload) -> None:
        # 🇩🇪 „Best effort“ – Fehler beim Bild sollen den Vorgang nicht stoppen
        code = getattr(unload, "barcode", None)
        if not code:
            return
        try:
            BarcodeGenerator(unload, code, "barcodes/unload").generate_image()
        except Exception:
            pass
