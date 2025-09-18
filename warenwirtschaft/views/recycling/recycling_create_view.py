# -*- coding: utf-8 -*-
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.forms.recycling_form import (
    UnloadChoiceForm,
    ExistingRecyclingForm,
    NewRecyclingFormSet,
)
from warenwirtschaft.models import Recycling
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    BARCODE_PREFIX = "A"  # Prefix für Recycling

    def get(self, request):
        # Aktive Fraktionen für die Tabelle laden
        active_qs = Recycling.objects.filter(status=1)

        # Alle sind initial ausgewählt
        initial_ids = list(active_qs.values_list("pk", flat=True))

        # Forms initialisieren
        unload_form = UnloadChoiceForm()
        existing_form = ExistingRecyclingForm(initial={"existing": active_qs})
        # Wichtig: konkreten QuerySet setzen
        existing_form.fields["existing"].queryset = active_qs

        new_formset = NewRecyclingFormSet(
            queryset=Recycling.objects.none(),
            prefix="new",
        )

        return self.render_page(
            unload_form=unload_form,
            existing_form=existing_form,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=[str(pk) for pk in initial_ids],  # "checked" im Template
            unload=None,
        )

    def post(self, request):
        active_qs = Recycling.objects.filter(status=1)

        # Formulare binden
        unload_form = UnloadChoiceForm(request.POST)
        existing_form = ExistingRecyclingForm(request.POST)
        existing_form.fields["existing"].queryset = active_qs  # Pflicht

        new_formset = NewRecyclingFormSet(
            request.POST,
            queryset=Recycling.objects.none(),
            prefix="new",
        )

        forms_ok = unload_form.is_valid() and existing_form.is_valid()
        formset_ok = new_formset.is_valid()

        if forms_ok and formset_ok:
            unload = unload_form.cleaned_data["unload"]
            selected_qs = existing_form.cleaned_data.get("existing")  # kann leer sein

            with transaction.atomic():
                # M2M-Links für aktive Fraktionen mit dem gewählten Unload synchronisieren
                current_ids = set(
                    Recycling.objects.filter(status=1, unloads=unload).values_list("pk", flat=True)
                )
                selected_ids = set(selected_qs.values_list("pk", flat=True)) if selected_qs is not None else set()

                to_add = selected_ids - current_ids
                to_remove = current_ids - selected_ids

                if to_add:
                    for r in Recycling.objects.filter(pk__in=to_add):
                        r.unloads.add(unload)
                if to_remove:
                    for r in Recycling.objects.filter(pk__in=to_remove):
                        r.unloads.remove(unload)

                # Neue Zeilen speichern und verknüpfen
                new_instances = new_formset.save(commit=False)
                for instance in new_instances:
                    # Pflicht-/Defaultwerte setzen, die nicht im Formular stehen
                    if not instance.status:
                        instance.status = 1  # aktiv

                    # Barcode nur erzeugen, wenn Feld faktisch leer ist
                    val = (getattr(instance, "barcode", "") or "").strip()
                    if not val:
                        instance.barcode = BarcodeNumberService.make_code(prefix=self.BARCODE_PREFIX)

                    instance.save()
                    instance.unloads.add(unload)

                # Unload-Status aktualisieren
                unload.status = 2
                unload.save(update_fields=["status"])

            return redirect(reverse("recycling_update", kwargs={"pk": unload.pk}))

        # Ungültig -> Seite mit Fehlern + beibehaltenen Auswahl-IDs
        existing_selected_ids = request.POST.getlist("existing")  # Feldname des MultipleChoice-Feldes
        unload_selected = unload_form.cleaned_data.get("unload") if unload_form.is_valid() else None

        return self.render_page(
            unload_form=unload_form,
            existing_form=existing_form,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=existing_selected_ids,
            unload=unload_selected,
        )

    # ---------- Hilfsmethoden ----------

    def render_page(self, unload_form, existing_form, new_formset, active_qs, existing_selected_ids, unload=None):
        # 'existing_selected_ids' als Set → Template kann "checked" schnell prüfen
        # 'existing_count' hilft bei der Nummerierung (erst bestehende, dann neue Zeilen)
        return render(self.request, self.template_name, {
            "unload_form": unload_form,
            "existing_form": existing_form,
            "new_formset": new_formset,
            "empty_form": new_formset.empty_form,   # für JS-Template (__prefix__)
            "active_qs": active_qs,                 # bestehende aktive Fraktionen für die Tabelle
            "existing_selected_ids": set(str(pk) for pk in existing_selected_ids),
            "existing_count": active_qs.count(),
            "unload": unload,
            "selected_menu": "recycling_create",
        })
