from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.forms.recycling_form import NewRecyclingFormSet
from warenwirtschaft.models import Recycling, Unload
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingUpdateView(View):
    template_name = "recycling/recycling_update.html"
    BARCODE_PREFIX = "A"  # Prefix für Recycling

    # ---------- GET ----------

    def get(self, request, pk):
        # Unload-Objekt holen oder 404 werfen
        unload = get_object_or_404(Unload, pk=pk)

        # Alle aktiven Recycling-Objekte
        active_qs = Recycling.objects.filter(status=Recycling.STATUS_AKTIV)

        # IDs der Recycling-Objekte, die bereits mit diesem Unload verknüpft sind
        existing_selected_ids = set(
            str(pk)
            for pk in unload.recycling_for_unload.filter(
                status=Recycling.STATUS_AKTIV
            ).values_list("pk", flat=True)
        )

        # Formset für neue Recycling-Zeilen (leer initial, nur über JS/HTML)
        new_formset = NewRecyclingFormSet(
            queryset=Recycling.objects.none(),
            prefix="new",
        )

        return self.render_page(
            unload=unload,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=existing_selected_ids,
        )

    # ---------- POST ----------

    def post(self, request, pk):
        unload = get_object_or_404(Unload, pk=pk)
        active_qs = Recycling.objects.filter(status=Recycling.STATUS_AKTIV)

        new_formset = NewRecyclingFormSet(
            request.POST,
            queryset=Recycling.objects.none(),
            prefix="new",
        )

        # Ausgewählte bestehende Recycling-IDs aus den Checkboxen
        existing_selected_ids = set(request.POST.getlist("existing"))

        if new_formset.is_valid():
            # String-IDs in int konvertieren (nur gültige Zahlen berücksichtigen)
            selected_ids = set()
            for value in existing_selected_ids:
                try:
                    selected_ids.add(int(value))
                except (TypeError, ValueError):
                    # Ungültige Werte ignorieren
                    continue

            with transaction.atomic():
                # --- Aktuelle Verknüpfungen (für diesen Unload + aktive Recycling) ---
                current_ids = set(
                    unload.recycling_for_unload.filter(
                        status=Recycling.STATUS_AKTIV
                    ).values_list("pk", flat=True)
                )

                to_add = selected_ids - current_ids
                to_remove = current_ids - selected_ids

                # Neue Verknüpfungen hinzufügen
                if to_add:
                    for r in Recycling.objects.filter(pk__in=to_add):
                        r.unloads.add(unload)

                # Verknüpfungen entfernen
                if to_remove:
                    for r in Recycling.objects.filter(pk__in=to_remove):
                        r.unloads.remove(unload)

                # --- Neue Recycling-Zeilen speichern und verknüpfen ---
                new_instances = new_formset.save(commit=False)

                for instance in new_instances:
                    # Standardstatus, falls nicht gesetzt
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

                # Unload-Status optional anpassen (idempotent):
                # z.B. sicherstellen, dass er auf "2" bleibt
                if unload.status != 2:
                    unload.status = 2
                    unload.save(update_fields=["status"])

            # Nach dem Speichern zurück auf dieselbe Seite (oder Liste, wie du willst)
            return redirect(reverse("recycling_update", kwargs={"pk": unload.pk}))

        # Fehler im Formset -> Seite mit Fehlern und aktueller Auswahl anzeigen
        return self.render_page(
            unload=unload,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=existing_selected_ids,
        )

    # ---------- Hilfsmethode ----------

    def render_page(self, unload, new_formset, active_qs, existing_selected_ids):
        return render(
            self.request,
            self.template_name,
            {
                "unload": unload,
                "new_formset": new_formset,
                "empty_form": new_formset.empty_form,  # für JS (__prefix__)
                "active_qs": active_qs,
                "existing_selected_ids": set(str(pk) for pk in existing_selected_ids),
                "existing_count": active_qs.count(),
                "selected_menu": "recycling_form",
            },
        )
