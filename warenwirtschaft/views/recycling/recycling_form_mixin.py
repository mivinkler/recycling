# warenwirtschaft/views/recycling/recycling_form_mixin.py
# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import render, get_object_or_404

from warenwirtschaft.forms.recycling_form import NewRecyclingFormSet
from warenwirtschaft.models import Recycling, Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingFormMixin:
    """
    Gemeinsame Helferfunktionen für Create/Update von Recycling-Einträgen.

    Aufgaben:
    - Basis-QuerySets bereitstellen
    - Formset für neue Recycling-Zeilen erzeugen
    - Standard-Status setzen
    - Barcodes erzeugen (analog zu Delivery/Unload)
    - neue Recycling-Objekte speichern und mit einem Unload verknüpfen
    - M2M-Verknüpfungen zwischen Unload und Recycling synchronisieren
    - einheitliches Context- und Rendering-Handling
    """

    BARCODE_PREFIX = "A"   # Prefix für Recycling
    new_prefix = "new"

    # ----------------------------------------------------------
    # Basis-Helfer
    # ----------------------------------------------------------
    def get_unload(self, pk: int) -> Unload:
        """
        Liefert den gewünschten Unload oder 404.
        """
        return get_object_or_404(Unload, pk=pk)

    def get_active_qs(self):
        """
        Liefert alle aktiven Recycling-Objekte.
        Aktiv bedeutet hier: is_active=True.
        """
        return (
            Recycling.objects
            .filter(is_active=True)
            .order_by("pk")
        )

    # ----------------------------------------------------------
    # Formset für neue Recycling-Zeilen
    # ----------------------------------------------------------
    def get_new_formset(self, data=None):
        """
        Liefert das Formset für neue Recycling-Zeilen (ohne Grund-QuerySet).

        Wichtig:
        - queryset=Recycling.objects.none() -> nur neue Objekte
        - prefix=self.new_prefix -> muss zu den Feldnamen im Template passen
        """
        kwargs = {
            "queryset": Recycling.objects.none(),
            "prefix": self.new_prefix,
        }
        if data is not None:
            kwargs["data"] = data
        return NewRecyclingFormSet(**kwargs)

    # ----------------------------------------------------------
    # Kontext + Rendering
    # ----------------------------------------------------------
    def get_context_data(self, **kwargs):
        """
        Basis-Kontext für Recycling-Seiten.

        Erwartet u.a.:
        - new_formset
        - active_qs
        - existing_selected_ids (Set von int-IDs)
        - unload oder unload_form (je nach View)
        """
        new_formset = kwargs.get("new_formset")
        active_qs = kwargs.get("active_qs")
        # 👉 Hier: IDs als int beibehalten, damit der Template-Vergleich mit obj.pk funktioniert
        existing_selected_ids = kwargs.get("existing_selected_ids", set())

        context = {
            "selected_menu": "recycling_form",
            "new_formset": new_formset,
            "empty_form": new_formset.empty_form if new_formset is not None else None,
            "active_qs": active_qs,
            # Set von int-IDs, wird direkt im Template mit obj.pk verglichen
            "existing_selected_ids": set(existing_selected_ids),
            "existing_count": active_qs.count() if active_qs is not None else 0,
            "unload": kwargs.get("unload"),
            "unload_form": kwargs.get("unload_form"),
        }
        context.update(kwargs)
        return context

    def render_response(self, request, context):
        """
        Rendert das aktuell gesetzte Template mit dem Kontext.
        Erwartet, dass die View self.template_name definiert.
        """
        return render(request, self.template_name, context)

    def form_invalid(self, request, **kwargs):
        """
        Einheitliche Behandlung bei ungültigen Formularen.
        """
        context = self.get_context_data(**kwargs)
        return self.render_response(request, context)

    # ----------------------------------------------------------
    # Standardwerte + Barcodes
    # ----------------------------------------------------------
    def _prepare_new_instances(self, instances):
        """
        Setzt Standard-Status und Barcodes für neue Recycling-Objekte.
        """
        # Standard-Status setzen, falls leer
        for obj in instances:
            if not obj.status:
                obj.status = StatusChoices.AUFBEREITUNG_LAUFEND

        # Barcodes über gemeinsamen Service setzen
        BarcodeNumberService.set_barcodes(
            instances,
            prefix=self.BARCODE_PREFIX,
        )

    # ----------------------------------------------------------
    # Speichern neuer Recycling-Zeilen
    # ----------------------------------------------------------
    def save_new_formset(self, formset, unload: Unload):
        """
        Speichert alle neuen Recycling-Objekte aus dem Formset
        und verknüpft sie mit dem übergebenen Unload.
        """
        instances = formset.save(commit=False)
        if not instances:
            return

        self._prepare_new_instances(instances)

        for obj in instances:
            obj.save()
            # Beziehung zum Unload setzen (M2M)
            obj.unloads.add(unload)

    # ----------------------------------------------------------
    # M2M-Verknüpfungen synchronisieren
    # ----------------------------------------------------------
    def sync_m2m(self, unload: Unload, selected_ids: set[int]):
        """
        Synchronisiert die M2M-Verknüpfungen zwischen Unload und
        aktiven Recycling-Objekten anhand der ausgewählten IDs.

        Nutzt is_active=True und das related_name 'recyclings'.
        """
        current_ids = set(
            unload.recyclings
            .filter(is_active=True)
            .values_list("pk", flat=True)
        )

        to_add = selected_ids - current_ids
        to_remove = current_ids - selected_ids

        if to_add:
            for r in Recycling.objects.filter(pk__in=to_add):
                r.unloads.add(unload)

        if to_remove:
            for r in Recycling.objects.filter(pk__in=to_remove):
                r.unloads.remove(unload)

    # ----------------------------------------------------------
    # Unload-Status
    # ----------------------------------------------------------
    def set_unload_status(self, unload: Unload, status: int = StatusChoices.AUFBEREITUNG_LAUFEND):
        """
        Setzt den Status des Unloads, falls abweichend.
        """
        if unload.status != status:
            unload.status = status
            unload.save(update_fields=["status"])

    # ----------------------------------------------------------
    # Transaktions-Helfer
    # ----------------------------------------------------------
    def atomic(self):
        """
        Kurzer Alias für transaction.atomic().
        """
        return transaction.atomic()
