from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.forms.recycling_form import (
    ExistingRecyclingForm,
    NewRecyclingFormSet,
)


class RecyclingUpdateView(View):
    """
    🇩🇪 Update-Ansicht für die Aufbereitung eines konkreten Unload:
    - Links (Checkboxen) zu allen aktiven Fraktionen (status=1) anzeigen.
      * Checkbox "existing" ist angehakt, wenn die Fraktion bereits mit dem Unload verknüpft ist.
      * Nutzer kann Häkchen entfernen/hinzufügen und speichern -> M2M wird synchronisiert.
    - Neue Fraktionen können über das Formset hinzugefügt und automatisch mit dem Unload verknüpft werden.
    - Layout/Interaktion identisch zu "create" (Tabellen-Design beibehalten).
    """
    template_name = "recycling/recycling_update.html"

    def get(self, request, pk: int):
        # 🇩🇪 Unload ermitteln
        unload = get_object_or_404(Unload, pk=pk)

        # 🇩🇪 Aktive Fraktionen (status=1)
        active_qs = Recycling.objects.filter(status=1)

        # 🇩🇪 IDs der derzeit mit diesem Unload verknüpften aktiven Fraktionen
        selected_ids_qs = Recycling.objects.filter(status=1, unloads=unload).values_list("pk", flat=True)
        selected_ids = set(selected_ids_qs)

        # 🇩🇪 Formular für bestehende Auswahl:
        # initial = aktuell verknüpfte Fraktionen
        existing_form = ExistingRecyclingForm(
            initial={"existing": active_qs.filter(unloads=unload)}
        )
        existing_form.fields["existing"].queryset = active_qs

        # 🇩🇪 Formset nur für NEUE Zeilen
        new_formset = NewRecyclingFormSet(queryset=Recycling.objects.none(), prefix="new")

        return self.render_page(
            existing_form=existing_form,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids={str(pk) for pk in selected_ids},
            unload=unload,
        )

    def post(self, request, pk: int):
        unload = get_object_or_404(Unload, pk=pk)
        active_qs = Recycling.objects.filter(status=1)

        # 🇩🇪 POST binden
        existing_form = ExistingRecyclingForm(request.POST)
        existing_form.fields["existing"].queryset = active_qs  # wichtig für Validierung

        new_formset = NewRecyclingFormSet(request.POST, queryset=Recycling.objects.none(), prefix="new")

        forms_ok = existing_form.is_valid()
        formset_ok = new_formset.is_valid()

        if forms_ok and formset_ok:
            selected_qs = existing_form.cleaned_data.get("existing")  # kann leer sein

            with transaction.atomic():
                # 🇩🇪 M2M-Synchronisierung nur innerhalb der aktiven Fraktionen
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

                # 🇩🇪 Neue Fraktionen speichern und mit Unload verknüpfen
                new_instances = new_formset.save(commit=False)
                for instance in new_instances:
                    # Pflicht-/Defaultwerte setzen, die nicht im Formular stehen
                    instance.status = 1  # aktiv
                    instance.save()
                    instance.unloads.add(unload)

                # 🇩🇪 Optional: Unload-Status sicherstellen (z.B. 2 = "in Aufbereitung")
                if getattr(unload, "status", None) != 2:
                    unload.status = 2
                    unload.save(update_fields=["status"])

            # 🇩🇪 Zur eigenen Update-Seite zurück
            return redirect(reverse("recycling_update", kwargs={"pk": unload.pk}))

        # 🇩🇪 Ungültig -> Auswahl erhalten
        selected_ids_post = request.POST.getlist("existing")
        return self.render_page(
            existing_form=existing_form,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=set(selected_ids_post),
            unload=unload,
        )

    def render_page(self, existing_form, new_formset, active_qs, existing_selected_ids, unload):
        # 🇩🇪 Hilfs-Renderer: liefert alle nötigen Kontextwerte an das Template
        return render(self.request, self.template_name, {
            "existing_form": existing_form,
            "new_formset": new_formset,
            "empty_form": new_formset.empty_form,    # für JS (__prefix__)
            "active_qs": active_qs,                  # aktive Fraktionen für die Tabelle
            "existing_selected_ids": existing_selected_ids,  # Set[str] für "checked"
            "existing_count": active_qs.count(),     # falls für die laufende Nummer benötigt
            "unload": unload,
            "selected_menu": "recycling_update",
        })
