# warenwirtschaft/views/recycling/recycling_update_view.py
# -*- coding: utf-8 -*-
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse

from warenwirtschaft.views.recycling.recycling_form_mixin import RecyclingFormMixin


class RecyclingUpdateView(RecyclingFormMixin, View):
    """
    Bearbeitung der Recycling-Fraktionen zu einem bestehenden Unload (Update-Fall).

    Schritte:
    - bestehende aktive Recycling-Objekte per Checkbox zuordnen/entfernen
    - neue Recycling-Objekte erfassen und mit dem Unload verknüpfen
    """

    template_name = "recycling/recycling_update.html"

    def get(self, request, pk: int):
        unload = self.get_unload(pk)
        active_qs = self.get_active_qs()

        existing_selected_ids = set(
            unload.recyclings
            .filter(is_active=True)
            .values_list("pk", flat=True)
        )

        new_formset = self.get_new_formset()

        context = self.get_context_data(
            unload=unload,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=existing_selected_ids,
        )
        return self.render_response(request, context)

    def post(self, request, pk: int):
        unload = self.get_unload(pk)
        active_qs = self.get_active_qs()

        new_formset = self.get_new_formset(data=request.POST)

        existing_selected_ids_raw = request.POST.getlist("existing")

        # 👉 сразу приводим к int
        selected_ids: set[int] = {
            int(value) for value in existing_selected_ids_raw if value.isdigit()
        }

        if new_formset.is_valid():
            with self.atomic():
                # M2M-Verknüpfungen aktualisieren
                self.sync_m2m(unload, selected_ids)

                # neue Recycling-Zeilen speichern
                self.save_new_formset(new_formset, unload)

                # Unload-Status anpassen
                self.set_unload_status(unload)

            return redirect(reverse("recycling_update", kwargs={"pk": unload.pk}))

        # Formset ist ungültig -> Seite mit Fehlern und gesetzten Checkboxen anzeigen
        context = self.get_context_data(
            unload=unload,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=selected_ids,
        )
        return self.render_response(request, context)

