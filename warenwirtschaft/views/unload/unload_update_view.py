# warenwirtschaft/views/unload/unload_update_view.py
# -*- coding: utf-8 -*-
from __future__ import annotations

from django.views import View
from django.shortcuts import redirect
from django.contrib import messages

from warenwirtschaft.forms.unload_form import ExistingEditFormSet
from warenwirtschaft.models import Unload
from warenwirtschaft.views.unload.unload_form_mixin import UnloadFormMixin


class UnloadUpdateView(UnloadFormMixin, View):
    """
    Bearbeitung der Vorsortierung zu einer Liefereinheit (Update-Fall).

    - Neue Unloads anlegen
    - Bestehende Unloads bearbeiten
    - Auswahl per Checkbox 'selected'
    """

    template_name = "unload/unload_update.html"

    # ----------------------------------------------------------
    # GET
    # ----------------------------------------------------------
    def get(self, request, delivery_unit_pk: int):
        delivery_unit = self.get_delivery_unit(delivery_unit_pk)

        formset = self.get_new_formset()
        vorhandene_forms = self._build_existing_forms(delivery_unit)

        context = self.get_context_data(
            delivery_unit=delivery_unit,
            formset=formset,
            vorhandene_forms=vorhandene_forms,
        )
        return self.render_response(request, context)

    # ----------------------------------------------------------
    # POST
    # ----------------------------------------------------------
    def post(self, request, delivery_unit_pk: int):
        delivery_unit = self.get_delivery_unit(delivery_unit_pk)

        formset = self.get_new_formset(data=request.POST)
        vorhandene_forms = self._build_existing_forms(
            delivery_unit,
            data=request.POST,
        )

        valid_new = formset.is_valid()
        valid_existing = all(f.is_valid() for f, _ in vorhandene_forms)

        if not (valid_new and valid_existing):
            messages.error(request, "⚠️ Bitte Eingaben prüfen.")
            context = self.get_context_data(
                delivery_unit=delivery_unit,
                formset=formset,
                vorhandene_forms=vorhandene_forms,
            )
            return self.render_response(request, context)

        # ausgewählte Unloads (aus Einzel-Forms)
        selected_ids = {
            str(f.instance.pk)
            for f, _ in vorhandene_forms
            if f.cleaned_data.get("selected")
        }

        # nur geänderte bestehende speichern
        changed_existing = [f for f, _ in vorhandene_forms if f.has_changed()]

        with self.atomic():
            # 1) bestehende Unloads speichern
            for f in changed_existing:
                f.save()

            # 2) M2M-Verknüpfung gemäß Auswahl
            for obj in Unload.objects.filter(
                is_active=True,
                status=self.OPEN_STATUS,
            ):
                if str(obj.pk) in selected_ids:
                    obj.delivery_units.add(delivery_unit)
                else:
                    obj.delivery_units.remove(delivery_unit)

            # 3) neue Unloads speichern + verknüpfen (inkl. Barcode)
            self.save_new_formset(formset, delivery_unit)

        messages.success(request, "✅ Die Daten sind gespeichert.")
        return redirect(self.get_success_url(delivery_unit.pk))

    # ----------------------------------------------------------
    # Aufbau der Einzel-Forms für bestehende Unloads
    # ----------------------------------------------------------
    def _build_existing_forms(self, delivery_unit, data=None):
        """
        Erstellt Einzel-Forms für alle offenen, aktiven Unloads.
        - GET: 'selected' kommt aus der M2M-Beziehung
        - POST: 'data' überschreibt initial automatisch
        """
        ExistingEditForm = ExistingEditFormSet.form

        selected_ids_db = set(
            Unload.objects
            .filter(delivery_units=delivery_unit, is_active=True)
            .values_list("pk", flat=True)
        )

        forms = []
        for obj in self.get_open_unloads_qs():
            form = ExistingEditForm(
                data=data if data is not None else None,
                instance=obj,
                prefix=f"exist_{obj.pk}",
                selected_initial=(obj.pk in selected_ids_db),
            )
            selected_flag = bool(form["selected"].value())
            forms.append((form, selected_flag))
        return forms
