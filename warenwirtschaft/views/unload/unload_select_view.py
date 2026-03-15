from django.shortcuts import redirect, render
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_scan_service import (
    BarcodeNotFoundError,
    BarcodeScanError,
    BarcodeScanService,
)


class UnloadSelectView(View):
    template_name = "unload/unload_select.html"

    def _context(self, *, scan_form=None):
        delivery_units_ready = (
            DeliveryUnit.objects.filter(
                status=StatusChoices.WARTET_AUF_VORSORTIERUNG,
            )
            .select_related("delivery", "delivery__customer", "material")
            .prefetch_related("unloads")
            .order_by("-pk")
        )

        delivery_units_active = (
            DeliveryUnit.objects.filter(
                status=StatusChoices.AKTIV_IN_VORSORTIERUNG,
            )
            .select_related("delivery", "delivery__customer", "material")
            .prefetch_related("unloads")
            .order_by("-pk")
        )

        return {
            "delivery_units_ready": delivery_units_ready,
            "delivery_units_active": delivery_units_active,
            "selected_menu": "unload_form",
            "scan_form": scan_form or BarcodeScanForm(),
        }

    def get(self, request):
        return render(request, self.template_name, self._context())

    def post(self, request):
        scan_form = BarcodeScanForm(request.POST)

        try:
            delivery_unit = BarcodeScanService.get_delivery_unit_for_unload(
                request.POST.get("scan_barcode")
            )
        except (BarcodeScanError, BarcodeNotFoundError) as exc:
            scan_form.add_error("scan_barcode", str(exc))
            return render(
                request,
                self.template_name,
                self._context(scan_form=scan_form),
            )

        return redirect("unload_create", delivery_unit_pk=delivery_unit.pk)
