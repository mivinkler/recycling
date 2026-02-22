from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.delivery_form import DeliveryForm, DeliveryUnitForm
from warenwirtschaft.models import Delivery, DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class DeliveryCreateView(View):
    template_name = "delivery/delivery_create.html"
    BARCODE_PREFIX = "L"

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _get_active_deliveries_with_all_units(self):
        """
        Zeigt Deliveries, die mindestens eine aktive DeliveryUnit (Status 1/2) haben,
        aber lädt und zeigt ALLE DeliveryUnits dieser Deliveries (auch andere Status).
        """
        active_statuses = [
            StatusChoices.WARTET_AUF_VORSORTIERUNG,
            StatusChoices.AKTIV_IN_VORSORTIERUNG,
        ]

        # 1) IDs von Deliveries finden, die mindestens eine aktive Unit haben
        delivery_ids = (
            DeliveryUnit.objects.filter(status__in=active_statuses)
            .values_list("delivery_id", flat=True)
            .distinct()
        )

        # 2) Deliveries laden + Customer
        deliveries = (
            Delivery.objects.filter(pk__in=delivery_ids)
            .select_related("customer")
            .prefetch_related("delivery_units")  # ALLE units dieser deliveries
            .order_by("pk")
        )

        return deliveries

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "delivery_form": DeliveryForm(),
                "unit_form": DeliveryUnitForm(),
                "active_deliveries": self._get_active_deliveries_with_all_units(),
            },
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request):
        delivery_form = DeliveryForm(request.POST)
        unit_form = DeliveryUnitForm(request.POST)

        if delivery_form.is_valid() and unit_form.is_valid():
            delivery = delivery_form.save()

            delivery_unit = unit_form.save(commit=False)
            delivery_unit.delivery = delivery

            BarcodeNumberService.set_barcodes([delivery_unit], prefix=self.BARCODE_PREFIX)
            delivery_unit.save()

            return redirect(reverse("delivery_update", kwargs={"delivery_pk": delivery.pk}))

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "delivery_form": delivery_form,
                "unit_form": unit_form,
                "active_deliveries": self._get_active_deliveries_with_all_units(),
            },
        )