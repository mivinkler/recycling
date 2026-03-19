from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.forms.delivery_form import (
    DeliveryForm,
    DeliveryUnitForm,
)
from warenwirtschaft.models import Delivery, DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_scan_service import (
    BarcodeNotFoundError,
    BarcodeScanError,
    BarcodeScanService,
)
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class DeliveryCreateView(View):
    template_name = "delivery/delivery_create.html"
    BARCODE_PREFIX = "L"
    GENERATED_BARCODE_FIELD_MAP = {
        "customer": "customer_id",
        "delivery_receipt": "delivery_receipt",
        "material": "material",
        "box_type": "box_type",
        "weight": "weight",
    }

    def _get_active_deliveries_with_all_units(self):
        active_statuses = [
            StatusChoices.WARTET_AUF_VORSORTIERUNG,
            StatusChoices.AKTIV_IN_VORSORTIERUNG,
        ]

        delivery_ids = (
            DeliveryUnit.objects.filter(status__in=active_statuses)
            .values_list("delivery_id", flat=True)
            .distinct()
        )

        return (
            Delivery.objects.filter(pk__in=delivery_ids)
            .select_related("customer")
            .prefetch_related("delivery_units")
            .order_by("pk")
        )

    def _render_page(self, request, *, delivery_form, unit_form, scan_form):
        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "delivery_form": delivery_form,
                "unit_form": unit_form,
                "scan_form": scan_form,
                "active_deliveries": self._get_active_deliveries_with_all_units(),
            },
        )

    def _should_handle_scan(self, request):
        barcode = (request.POST.get("scan_barcode") or "").strip()
        return bool(barcode) and request.POST.get("action") != "save"

    def _set_default_value(self, form_data, field_name, value):
        if value in (None, ""):
            return

        current_value = form_data.get(field_name, "")
        if isinstance(current_value, str):
            current_value = current_value.strip()

        if current_value:
            return

        form_data[field_name] = str(value)

    def _build_prefilled_forms(self, post_data):
        form_data = post_data.copy()
        barcode_data = BarcodeScanService.get_generated_prefill_data(
            form_data.get("scan_barcode")
        )

        for form_field, barcode_field in self.GENERATED_BARCODE_FIELD_MAP.items():
            self._set_default_value(
                form_data, form_field, barcode_data.get(barcode_field)
            )

        form_data["scan_barcode"] = ""
        return (
            DeliveryForm(form_data),
            DeliveryUnitForm(form_data),
            BarcodeScanForm(),
        )

    def get(self, request):
        return self._render_page(
            request,
            delivery_form=DeliveryForm(),
            unit_form=DeliveryUnitForm(),
            scan_form=BarcodeScanForm(),
        )

    def post(self, request):
        if self._should_handle_scan(request):
            try:
                delivery_form, unit_form, scan_form = self._build_prefilled_forms(
                    request.POST
                )
            except (BarcodeScanError, BarcodeNotFoundError) as exc:
                delivery_form = DeliveryForm(request.POST)
                unit_form = DeliveryUnitForm(request.POST)
                scan_form = BarcodeScanForm(request.POST)
                scan_form.add_error("scan_barcode", str(exc))

            return self._render_page(
                request,
                delivery_form=delivery_form,
                unit_form=unit_form,
                scan_form=scan_form,
            )

        delivery_form = DeliveryForm(request.POST)
        unit_form = DeliveryUnitForm(request.POST)
        scan_form = BarcodeScanForm()

        if delivery_form.is_valid() and unit_form.is_valid():
            delivery = delivery_form.save()

            delivery_unit = unit_form.save(commit=False)
            delivery_unit.delivery = delivery

            BarcodeNumberService.set_barcodes(
                [delivery_unit], prefix=self.BARCODE_PREFIX
            )
            delivery_unit.save()

            return redirect(
                reverse(
                    "delivery_unit_new",
                    kwargs={
                        "delivery_pk": delivery.pk,
                    },
                )
            )

        return self._render_page(
            request,
            delivery_form=delivery_form,
            unit_form=unit_form,
            scan_form=scan_form,
        )
