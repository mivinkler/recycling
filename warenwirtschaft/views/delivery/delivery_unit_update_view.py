from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.delivery_form import DeliveryUnitForm
from warenwirtschaft.models import Delivery, DeliveryUnit
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class DeliveryUnitUpdateView(View):
    template_name = "delivery/delivery_unit_update.html"
    BARCODE_PREFIX = "L"

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _get_delivery(self, delivery_pk):
        # Lädt die Delivery oder wirft 404.
        return get_object_or_404(Delivery, pk=delivery_pk)

    def _get_delivery_units(self, delivery):
        # Lädt alle Liefereinheiten zur Delivery.
        return DeliveryUnit.objects.filter(delivery=delivery).order_by("pk")

    def _get_edit_unit(self, delivery, delivery_unit_pk):
        # Lädt die zu bearbeitende Liefereinheit (muss zur Delivery gehören).
        if delivery_unit_pk is None:
            return None
        return get_object_or_404(DeliveryUnit, pk=delivery_unit_pk, delivery=delivery)

    def _render_page(self, request, delivery, delivery_units, unit_form, edit_unit):
        # Rendert die Seite (Liste + Formular).
        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "delivery": delivery,
                "delivery_units": delivery_units,
                "unit_form": unit_form,
                "edit_unit": edit_unit,
            },
        )

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, delivery_pk, delivery_unit_pk=None, *args, **kwargs):
        delivery = self._get_delivery(delivery_pk)
        delivery_units = self._get_delivery_units(delivery)
        edit_unit = self._get_edit_unit(delivery, delivery_unit_pk)

        # Wenn edit_unit gesetzt ist, wird die Zeile bearbeitet, sonst neue Zeile anlegen
        unit_form = DeliveryUnitForm(instance=edit_unit)

        return self._render_page(request, delivery, delivery_units, unit_form, edit_unit)

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, delivery_pk, delivery_unit_pk=None, *args, **kwargs):
        delivery = self._get_delivery(delivery_pk)
        delivery_units = self._get_delivery_units(delivery)
        edit_unit = self._get_edit_unit(delivery, delivery_unit_pk)

        # Update (instance=edit_unit) oder Create (instance=None)
        unit_form = DeliveryUnitForm(request.POST, instance=edit_unit)

        if unit_form.is_valid():
            unit = unit_form.save(commit=False)

            # Bei neuer Liefereinheit: Delivery setzen + Barcode vergeben
            if edit_unit is None:
                unit.delivery = delivery
                BarcodeNumberService.set_barcodes([unit], prefix=self.BARCODE_PREFIX)

            unit.save()
            return redirect(reverse("delivery_unit_new", kwargs={"delivery_pk": delivery.pk}))

        # Bei Fehlern die Seite mit Fehlermeldungen erneut anzeigen
        return self._render_page(request, delivery, delivery_units, unit_form, edit_unit)