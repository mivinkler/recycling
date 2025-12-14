# warenwirtschaft/views/recycling/recycling_create_view.py
from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from warenwirtschaft.forms.recycling_form import NewRecyclingFormSet
from warenwirtschaft.models import Recycling, Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingCreateView(View):
    """
    Ein Screen für Anlage/Bearbeitung der Recycling-Fraktionen eines Unloads.
    """

    template_name = "recycling/recycling_create.html"
    NEW_PREFIX = "new"          # Muss zu Template/JS passen
    BARCODE_PREFIX = "A"
    NEW_FIELDS = ("material", "box_type", "weight", "note")

    def get(self, request, unload_pk: int):
        unload = self._get_unload(unload_pk)
        active_qs = Recycling.objects.filter(is_active=True).order_by("pk")
        selected_ids = self._selected_ids_db(unload)
        formset = self._formset()

        return self._render(request, unload, active_qs, selected_ids, formset)

    def post(self, request, unload_pk: int):
        unload = self._get_unload(unload_pk)
        active_qs = Recycling.objects.filter(is_active=True).order_by("pk")
        selected_ids = self._selected_ids_post(request)
        formset = self._formset(data=request.POST)

        if formset.is_valid():
            with transaction.atomic():
                self._sync_m2m(unload, selected_ids)
                self._save_new_rows(formset, unload)
                self._ensure_unload_status(unload)

            return redirect("recycling_create", unload_pk=unload.pk)

        return self._render(request, unload, active_qs, selected_ids, formset)

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------
    def _render(self, request, unload: Unload, active_qs, selected_ids: set[int], formset):
        """Rendert das Template mit Standard-Context."""
        return render(request, self.template_name, {
            "selected_menu": "recycling_form",
            "unload": unload,
            "active_qs": active_qs,
            "existing_selected_ids": selected_ids,
            "existing_count": active_qs.count(),
            "new_formset": formset,
        })

    def _get_unload(self, pk: int) -> Unload:
        """Liefert Unload oder 404."""
        return get_object_or_404(Unload, pk=pk)

    def _selected_ids_db(self, unload: Unload) -> set[int]:
        """IDs der bereits verknüpften aktiven Recycling-Objekte."""
        return set(unload.recyclings.filter(is_active=True).values_list("pk", flat=True))

    def _selected_ids_post(self, request) -> set[int]:
        """Checkbox-Auswahl aus POST (name='existing') als Set[int]."""
        raw = request.POST.getlist("existing")
        return {int(v) for v in raw if v.isdigit()}

    def _formset(self, data=None):
        """Formset für neue Recycling-Zeilen (nur neue Objekte)."""
        return NewRecyclingFormSet(
            data=data,
            queryset=Recycling.objects.none(),
            prefix=self.NEW_PREFIX,
        )

    # ----------------------------------------------------------
    # Speichern: neue Zeilen
    # ----------------------------------------------------------
    def _prepare_new_instances(self, instances: list[Recycling]) -> None:
        """Setzt Standard-Status und Barcodes für neue Recycling-Objekte."""
        for obj in instances:
            obj.status = obj.status or StatusChoices.IN_AUFBEREITUNG

        BarcodeNumberService.set_barcodes(instances, prefix=self.BARCODE_PREFIX)

    def _save_new_rows(self, formset, unload: Unload) -> None:
        """Speichert neue Recycling-Zeilen und verknüpft sie mit dem Unload."""
        created: list[Recycling] = []

        for form in formset.forms:
            cd = form.cleaned_data
            if not any(cd.get(k) not in ("", None) for k in self.NEW_FIELDS):
                continue
            created.append(form.save(commit=False))

        if not created:
            return

        self._prepare_new_instances(created)

        for obj in created:
            obj.save()

        unload.recyclings.add(*created)

    # ----------------------------------------------------------
    # M2M + Status
    # ----------------------------------------------------------
    def _sync_m2m(self, unload: Unload, selected_ids: set[int]) -> None:
        """
        Synchronisiert die M2M-Verknüpfungen für aktive Recycling-Objekte.
        Inaktive Verknüpfungen bleiben unangetastet.
        """
        current_ids = self._selected_ids_db(unload)

        to_add = selected_ids - current_ids
        to_remove = current_ids - selected_ids

        if to_add:
            unload.recyclings.add(*to_add)
        if to_remove:
            unload.recyclings.remove(*to_remove)

    def _ensure_unload_status(self, unload: Unload) -> None:
        """Setzt den Status des Unloads, falls abweichend."""
        target = StatusChoices.IN_AUFBEREITUNG
        if unload.status != target:
            unload.status = target
            unload.save(update_fields=["status"])
