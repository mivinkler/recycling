# warenwirtschaft/views/recycling/recycling_create_view.py
# -*- coding: utf-8 -*-
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse

from warenwirtschaft.views.recycling.recycling_form_mixin import RecyclingFormMixin


class RecyclingCreateView(RecyclingFormMixin, View):
    """
    Anlage / erste Pflege der Recycling-Fraktionen zu einem Unload (Create-Fall).

    Schritte:
    - bestehende aktive Recycling-Objekte per Checkbox zuordnen/entfernen
    - neue Recycling-Objekte erfassen und mit dem Unload verknüpfen
    """

    template_name = "recycling/recycling_create.html"

    # ----------------------------------------------------------
    # GET
    # ----------------------------------------------------------
    def get(self, request, unload_pk: int):
        unload = self.get_unload(unload_pk)
        active_qs = self.get_active_qs()

        # bereits verknüpfte aktive Recycling-Objekte (meist leer bei AUSSTEHEND)
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

    # ----------------------------------------------------------
    # POST
    # ----------------------------------------------------------
    def post(self, request, unload_pk: int):
        unload = self.get_unload(unload_pk)
        active_qs = self.get_active_qs()

        new_formset = self.get_new_formset(data=request.POST)

        # Ausgewählte bestehende Recycling-IDs aus den Checkboxen
        existing_selected_ids_raw = request.POST.getlist("existing")

        if new_formset.is_valid():
            selected_ids: set[int] = set()
            for value in existing_selected_ids_raw:
                if value.isdigit():
                    selected_ids.add(int(value))

            with self.atomic():
                # M2M-Verknüpfungen für aktive Recycling-Objekte synchronisieren
                self.sync_m2m(unload, selected_ids)

                # Neue Recycling-Zeilen speichern und mit Unload verknüpfen
                self.save_new_formset(new_formset, unload)

                # Unload-Status anpassen (z.B. AUFBEREITUNG_LAUFEND)
                self.set_unload_status(unload)

            return redirect(reverse("recycling_update", kwargs={"pk": unload.pk}))

        # Formularfehler -> Seite erneut anzeigen, Auswahl beibehalten
        return self.form_invalid(
            request,
            unload=unload,
            new_formset=new_formset,
            active_qs=active_qs,
            existing_selected_ids=set(existing_selected_ids_raw),
        )
