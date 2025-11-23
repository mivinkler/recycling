from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.forms.recycling_form import (
    UnloadChoiceForm,
    NewRecyclingFormSet,
)
from warenwirtschaft.models import Recycling
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    BARCODE_PREFIX = "A"  # Prefix für Recycling

    # ---------- GET ----------

    def get(self, request):
        # Aktive Fraktionen laden (bei Bedarf Filter anpassen)
        active_qs = Recycling.objects.filter(status=Recycling.STATUS_AKTIV)

        # Alle aktiven Recycling-Objekte sind initial ausgewählt
        existing_selected_ids = {
            str(pk) for pk in active_qs.values_list("pk", flat=True)
        }

        unload_form = UnloadChoiceForm()

        new_formset = NewRecyclingFormSet(
            queryset=Recycling.objects.none(),
            prefix="new",
        )

        return self.render_page(
            unload_form=unload_form,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=existing_selected_ids,
            unload=None,
        )

    # ---------- POST ----------

    def post(self, request):
        active_qs = Recycling.objects.filter(status=Recycling.STATUS_AKTIV)

        unload_form = UnloadChoiceForm(request.POST)
        new_formset = NewRecyclingFormSet(
            request.POST,
            queryset=Recycling.objects.none(),
            prefix="new",
        )

        # Ausgewählte bestehende Recycling-IDs aus den Checkboxen lesen
        existing_selected_ids = set(request.POST.getlist("existing"))

        if unload_form.is_valid() and new_formset.is_valid():
            unload = unload_form.cleaned_data["unload"]

            # String-IDs in int konvertieren (für DB-Abfragen)
            selected_ids = {int(pk) for pk in existing_selected_ids}

            with transaction.atomic():
                # --- M2M-Verknüpfungen für aktive Recycling-Objekte synchronisieren ---
                current_ids = set(
                    Recycling.objects.filter(
                        status=Recycling.STATUS_AKTIV,
                        unloads=unload,
                    ).values_list("pk", flat=True)
                )

                to_add = selected_ids - current_ids
                to_remove = current_ids - selected_ids

                if to_add:
                    for r in Recycling.objects.filter(pk__in=to_add):
                        # Nur diesen Unload hinzufügen, andere Verknüpfungen bleiben
                        r.unloads.add(unload)

                if to_remove:
                    for r in Recycling.objects.filter(pk__in=to_remove):
                        r.unloads.remove(unload)

                # --- Neue Recycling-Zeilen speichern und mit Unload verknüpfen ---
                new_instances = new_formset.save(commit=False)

                for instance in new_instances:
                    # Standardstatus setzen, falls im Formular nicht gesetzt
                    if not instance.status:
                        instance.status = Recycling.STATUS_AKTIV

                    # Barcode nur erzeugen, wenn Feld leer ist
                    val = (getattr(instance, "barcode", "") or "").strip()
                    if not val:
                        instance.barcode = BarcodeNumberService.make_code(
                            prefix=self.BARCODE_PREFIX
                        )

                    instance.save()
                    instance.unloads.add(unload)

                # Unload-Status anpassen (falls gewünscht)
                unload.status = 2
                unload.save(update_fields=["status"])

            return redirect(reverse("recycling_update", kwargs={"pk": unload.pk}))

        # Formularfehler -> Seite erneut anzeigen, Auswahl beibehalten
        unload_selected = (
            unload_form.cleaned_data.get("unload")
            if unload_form.is_valid()
            else None
        )

        return self.render_page(
            unload_form=unload_form,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=existing_selected_ids,
            unload=unload_selected,
        )

    # ---------- Hilfsmethode ----------

    def render_page(
        self,
        unload_form,
        new_formset,
        active_qs,
        existing_selected_ids,
        unload=None,
    ):
        return render(
            self.request,
            self.template_name,
            {
                "unload_form": unload_form,
                "new_formset": new_formset,
                "empty_form": new_formset.empty_form,  # für JS (__prefix__)
                "active_qs": active_qs,                # bestehende aktive Fraktionen
                "existing_selected_ids": set(
                    str(pk) for pk in existing_selected_ids
                ),
                "existing_count": active_qs.count(),
                "unload": unload,
                "selected_menu": "recycling_form",
            },
        )
