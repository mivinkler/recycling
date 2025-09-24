from __future__ import annotations

from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.forms.unload_form import DeliveryUnitForm, ExistingEditFormSet, UnloadFormSet
from warenwirtschaft.models import Unload
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class UnloadCreateView(View):
    template_name = "unload/unload_create.html"
    BARCODE_PREFIX = "S"  # Prefix für Vorsortierung/Unload

    def get(self, request):
        # Kopf-Form + leeres FormSet für neue Unloads
        form = DeliveryUnitForm()
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")

        # Aktive Wagen (vorhandene Unloads) + FormSet für deren Edit
        vorhandene_unloads = Unload.objects.filter(status=1).order_by("pk")
        existing_formset = ExistingEditFormSet(
            queryset=vorhandene_unloads, prefix="exist"
        )

        return self.render_page(form, formset, vorhandene_unloads, existing_formset)

    def post(self, request):
        # Kopf-Form binden
        delivery_form = DeliveryUnitForm(request.POST)
        # Neue Zeilen binden (nur neue Datensätze)
        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")
        # Vorhandene Zeilen binden (Status/Gewicht)
        vorhandene_unloads_qs = Unload.objects.filter(status=1).order_by("pk")
        existing_formset = ExistingEditFormSet(
            request.POST, queryset=vorhandene_unloads_qs, prefix="exist"
        )

        # Auswahl aus Checkboxen (bestehende Unloads, die verknüpft werden sollen)
        selected_ids = request.POST.getlist("selected_unload")

        if delivery_form.is_valid():
            delivery_unit = delivery_form.cleaned_data["delivery_unit"]

            has_new_rows = formset.total_form_count() > 0
            # Validierung nur dort, wo es Eingaben gibt
            if has_new_rows and not formset.is_valid():
                return self.render_page(delivery_form, formset, vorhandene_unloads_qs, existing_formset)

            if not existing_formset.is_valid():
                # Fehler in bestehenden Zeilen anzeigen
                return self.render_page(delivery_form, formset, vorhandene_unloads_qs, existing_formset)

            with transaction.atomic():
                # 1) Bestehende Unloads mit Liefereinheit VERKNÜPFEN (nur hinzufügen)
                if selected_ids:
                    selected_pks: list[int] = []
                    for pk in selected_ids:
                        try:
                            selected_pks.append(int(pk))
                        except (TypeError, ValueError):
                            # Ignoriere ungültige IDs im POST
                            pass
                    for unload in Unload.objects.filter(status=1, pk__in=selected_pks):
                        unload.delivery_units.add(delivery_unit)  # idempotent

                # 2) Bestehende Unloads (Status/Gewicht) speichern
                #     Nur die beiden Felder sind im Form; M2M bleibt unberührt.
                existing_formset.save()

                # 3) Neue Unloads speichern + mit Liefereinheit verknüpfen
                if has_new_rows:
                    new_instances = formset.save(commit=False)
                    for instance in new_instances:
                        # Standard-Status, falls leer
                        if not instance.status:
                            instance.status = 1

                        # Barcode nur erzeugen, wenn Feld faktisch leer ist
                        val = (getattr(instance, "barcode", "") or "").strip()
                        if not val:
                            instance.barcode = BarcodeNumberService.marke_code(prefix=self.BARCODE_PREFIX)

                        instance.save()
                        instance.delivery_units.add(delivery_unit)

            return redirect(reverse("unload_update", kwargs={"delivery_unit_pk": delivery_unit.pk}))

        # Ungültige Liefereinheit -> Seite neu anzeigen
        vorhandene_unloads = Unload.objects.filter(status=1).order_by("pk")
        return self.render_page(delivery_form, formset, vorhandene_unloads, existing_formset)

    # ---------- Hilfsmethoden ----------

    def render_page(self, form, formset, vorhandene_unloads, existing_formset):
        # Zentrales Rendering – inkl. existing_formset
        return render(self.request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_unloads": vorhandene_unloads,  # für Anzeige (Material/Behälter)
            "existing_formset": existing_formset,      # für Status/Gewicht-Inputs
            "selected_menu": "unload_create",
        })
