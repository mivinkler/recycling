# warenwirtschaft/views/unload/unload_create_view.py
# -*- coding: utf-8 -*-
from __future__ import annotations

from django.views import View
from django.shortcuts import redirect

from warenwirtschaft.forms.unload_form import ExistingEditFormSet
from warenwirtschaft.models import Unload
from warenwirtschaft.views.unload.unload_form_mixin import UnloadFormMixin


class UnloadCreateView(UnloadFormMixin, View):
    """
    Erfassung der Vorsortierung für eine Liefereinheit (Create-Fall).

    - Neue Unloads anlegen
    - Bestehende offene Unloads mit der Liefereinheit verknüpfen
    """

    template_name = "unload/unload_create.html"

    # ----------------------------------------------------------
    # GET
    # ----------------------------------------------------------
    def get(self, request, delivery_unit_pk: int):
        delivery_unit = self.get_delivery_unit(delivery_unit_pk)

        formset = self.get_new_formset()
        offene_unloads_qs = self.get_open_unloads_qs()
        existing_formset = ExistingEditFormSet(
            queryset=offene_unloads_qs,
            prefix="exist",
        )

        context = self.get_context_data(
            delivery_unit=delivery_unit,
            formset=formset,
            vorhandene_unloads=offene_unloads_qs,
            existing_formset=existing_formset,
        )
        return self.render_response(request, context)

    # ----------------------------------------------------------
    # POST
    # ----------------------------------------------------------
    def post(self, request, delivery_unit_pk: int):
        delivery_unit = self.get_delivery_unit(delivery_unit_pk)

        formset = self.get_new_formset(data=request.POST)

        offene_unloads_qs = self.get_open_unloads_qs()
        existing_formset = ExistingEditFormSet(
            data=request.POST,
            queryset=offene_unloads_qs,
            prefix="exist",
        )

        # ausgewählte bestehende Unloads (Checkboxen)
        selected_pks = {
            int(pk) for pk in request.POST.getlist("selected_unload") if pk.isdigit()
        }

        has_new_rows = formset.total_form_count() > 0

        # Validierung: neue + bestehende Einträge
        if (has_new_rows and not formset.is_valid()) or not existing_formset.is_valid():
            return self.form_invalid(
                request,
                delivery_unit,
                formset,
                vorhandene_unloads=offene_unloads_qs,
                existing_formset=existing_formset,
            )

        with self.atomic():
            # 1) bestehende Unloads speichern
            existing_formset.save()

            # 2) M2M-Verknüpfung für ausgewählte bestehende Unloads
            if selected_pks:
                for unload in offene_unloads_qs.filter(pk__in=selected_pks):
                    unload.delivery_units.add(delivery_unit)

            # 3) neue Unloads speichern + verknüpfen (inkl. Barcode)
            if has_new_rows:
                self.save_new_formset(formset, delivery_unit)

        return redirect(self.get_success_url(delivery_unit.pk))
