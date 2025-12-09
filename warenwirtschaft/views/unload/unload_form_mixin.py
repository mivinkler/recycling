# warenwirtschaft/views/unload/unload_form_mixin.py
# -*- coding: utf-8 -*-
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from warenwirtschaft.forms.unload_form import UnloadFormSet
from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class UnloadFormMixin:
    """
    Gemeinsame Helferfunktionen für Create/Update von Unloads
    zu einer Liefereinheit.

    Aufgaben:
    - Basis-QuerySets und Liefereinheit laden
    - Formset für neue Unloads bereitstellen
    - Standard-Status setzen
    - Barcodes erzeugen (wie bei Delivery)
    - neue Unloads speichern und mit der Liefereinheit verknüpfen
    - einheitliche Kontext- und Fehlerbehandlung
    """

    OPEN_STATUS = StatusChoices.VORSORTIERUNG_LAUFEND
    BARCODE_PREFIX = "S"
    new_prefix = "new"

    # ----------------------------------------------------------
    # Basis-Helfer
    # ----------------------------------------------------------
    def get_delivery_unit(self, delivery_unit_pk: int) -> DeliveryUnit:
        """
        Liefert die zugehörige Liefereinheit oder 404.
        """
        return get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

    def get_open_unloads_qs(self):
        """
        Basis-Query für alle offenen, aktiven Unloads.
        """
        return (
            Unload.objects
            .filter(is_active=True, status=self.OPEN_STATUS)
            .order_by("pk")
        )

    # ----------------------------------------------------------
    # Formset für neue Unloads
    # ----------------------------------------------------------
    def get_new_formset(self, data=None):
        """
        Liefert das Formset für neue Unloads (ohne Grund-QuerySet).
        """
        kwargs = {
            "queryset": Unload.objects.none(),
            "prefix": self.new_prefix,
        }
        if data is not None:
            kwargs["data"] = data
        return UnloadFormSet(**kwargs)

    # ----------------------------------------------------------
    # Kontext + Rendering
    # ----------------------------------------------------------
    def get_context_data(self, **kwargs):
        """
        Basis-Kontext für Unload-Formseiten.
        Kann in den Views über **kwargs erweitert werden.
        """
        formset = kwargs.get("formset")

        context = {
            "delivery_unit": kwargs.get("delivery_unit"),
            "formset": formset,
            "empty_form": formset.empty_form if formset is not None else None,
            "selected_menu": "unload_form",
        }
        context.update(kwargs)
        return context

    def render_response(self, request, context):
        """
        Rendert das aktuell konfigurierte Template mit dem Kontext.
        Erwartet, dass die View self.template_name setzt.
        """
        return render(request, self.template_name, context)

    def form_invalid(self, request, delivery_unit, formset, **extra_context):
        """
        Einheitliche Behandlung von ungültigen Formularen.
        """
        context = self.get_context_data(
            delivery_unit=delivery_unit,
            formset=formset,
            **extra_context,
        )
        return self.render_response(request, context)

    # ----------------------------------------------------------
    # Standardwerte + Barcodes
    # ----------------------------------------------------------
    def _prepare_new_unloads(self, instances):
        """
        Setzt Standard-Status und Barcodes für neue Unloads.
        Die Barcode-Logik entspricht der von Delivery.
        """
        # Standard-Status setzen, falls leer
        for obj in instances:
            if not obj.status:
                obj.status = self.OPEN_STATUS

        # Barcodes über gemeinsamen Service setzen
        BarcodeNumberService.set_barcodes(
            instances,
            prefix=self.BARCODE_PREFIX,
        )

    # ----------------------------------------------------------
    # Speichern der neuen Unloads
    # ----------------------------------------------------------
    def save_new_formset(self, formset, delivery_unit: DeliveryUnit):
        """
        Speichert alle neuen Unloads aus dem Formset und verknüpft sie
        mit der übergebenen Liefereinheit.
        """
        instances = formset.save(commit=False)
        if not instances:
            return

        self._prepare_new_unloads(instances)

        for obj in instances:
            obj.save()
            obj.delivery_units.add(delivery_unit)

        # Für den Fall, dass can_delete=True wäre:
        if hasattr(formset, "deleted_objects"):
            for deleted in formset.deleted_objects:
                deleted.delete()

    # ----------------------------------------------------------
    # Transaktions- und Redirect-Helfer
    # ----------------------------------------------------------
    def atomic(self):
        """
        Kurzer Alias für transaction.atomic().
        """
        return transaction.atomic()

    def get_success_url(self, delivery_unit_pk: int) -> str:
        """
        Erfolgs-URL: immer zurück auf die Update-Seite.
        """
        return reverse("unload_update", kwargs={"delivery_unit_pk": delivery_unit_pk})
