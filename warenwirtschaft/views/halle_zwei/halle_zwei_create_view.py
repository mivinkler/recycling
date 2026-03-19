from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models.halle_zwei import HalleZwei
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_scan_service import (
    BarcodeNotFoundError,
    BarcodeScanError,
    BarcodeScanService,
)


class HalleZweiCreateView(View):
    template_name = "halle_zwei/halle_zwei_create.html"

    def _delivery_units_ready(self):
        return DeliveryUnit.objects.filter(
            status=StatusChoices.WARTET_AUF_HALLE_ZWEI
        ).order_by("pk")

    def _today_checked(self):
        return (
            HalleZwei.objects.filter(delivery_unit__status=StatusChoices.ERLEDIGT)
            .select_related("delivery_unit")
            .order_by("-created_at")
        )

    def _context(self, *, scan_form=None):
        return {
            "delivery_unit_ready": self._delivery_units_ready(),
            "today_checked": self._today_checked(),
            "scan_form": scan_form or BarcodeScanForm(),
        }

    def get(self, request):
        return render(request, self.template_name, self._context())

    def _mark_checked(self, delivery_unit):
        halle_zwei, _ = HalleZwei.objects.get_or_create(
            delivery_unit=delivery_unit,
            defaults={
                "status": StatusChoices.WARTET_AUF_ABHOLUNG,
                "halle_zwei": True,
            },
        )
        if (
            halle_zwei.status != StatusChoices.WARTET_AUF_ABHOLUNG
            or not halle_zwei.halle_zwei
        ):
            halle_zwei.status = StatusChoices.WARTET_AUF_ABHOLUNG
            halle_zwei.halle_zwei = True
            halle_zwei.save(update_fields=["status", "halle_zwei"])

        delivery_unit.status = StatusChoices.ERLEDIGT
        delivery_unit.inactive_at = timezone.now()
        delivery_unit.save(update_fields=["status", "inactive_at"])

    def _mark_unchecked(self, delivery_unit):
        HalleZwei.objects.filter(delivery_unit=delivery_unit).delete()

        delivery_unit.status = StatusChoices.WARTET_AUF_HALLE_ZWEI
        delivery_unit.inactive_at = None
        delivery_unit.save(update_fields=["status", "inactive_at"])

    @transaction.atomic
    def post(self, request):
        action = request.POST.get("action")

        if action == "scan_check":
            scan_form = BarcodeScanForm(request.POST)

            try:
                delivery_unit = BarcodeScanService.get_delivery_unit_for_halle_zwei(
                    request.POST.get("scan_barcode")
                )
            except (BarcodeScanError, BarcodeNotFoundError) as exc:
                scan_form.add_error("scan_barcode", str(exc))
                return render(
                    request,
                    self.template_name,
                    self._context(scan_form=scan_form),
                )

            self._mark_checked(delivery_unit)
            return redirect("halle_zwei_create")

        if action == "check":
            delivery_unit_id = request.POST.get("delivery_unit_id")
            delivery_unit = DeliveryUnit.objects.filter(
                pk=delivery_unit_id,
                status=StatusChoices.WARTET_AUF_HALLE_ZWEI,
            ).first()
            if delivery_unit:
                self._mark_checked(delivery_unit)
        elif action == "uncheck":
            delivery_unit_id = request.POST.get("delivery_unit_id")
            delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_id)
            self._mark_unchecked(delivery_unit)

        return redirect("halle_zwei_create")
