from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.recycling_page_mixin import RecyclingPageMixin
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService
from warenwirtschaft.services.barcode_scan_service import (
    BarcodeNotFoundError,
    BarcodeScanError,
    BarcodeScanService,
)


class RecyclingCreateView(RecyclingPageMixin, View):
    BARCODE_PREFIX = "Z"

    def _attach_unload(self, unload):
        for recycling in self._get_recyclings_in_progress():
            recycling.unloads.add(unload)

        unload.status = StatusChoices.ERLEDIGT
        unload.inactive_at = timezone.now()
        unload.save(update_fields=["status", "inactive_at"])

    def _reset_unload(self, unload):
        unload.status = StatusChoices.WARTET_AUF_ZERLEGUNG
        unload.inactive_at = None
        unload.save(update_fields=["status", "inactive_at"])

    def _get_finished_unload(self, unload_id):
        return get_object_or_404(
            Unload,
            pk=int(unload_id),
            status=StatusChoices.ERLEDIGT,
        )

    def _get_ready_unload(self, unload_id):
        return get_object_or_404(
            Unload,
            pk=int(unload_id),
            status=StatusChoices.WARTET_AUF_ZERLEGUNG,
        )

    def get(self, request):
        return render(request, self.template_name, self._build_context())

    def post(self, request):
        if request.POST.get("action") == "scan_unload":
            scan_form = BarcodeScanForm(request.POST)

            try:
                unload = BarcodeScanService.get_unload_for_recycling(
                    request.POST.get("scan_barcode")
                )
            except (BarcodeScanError, BarcodeNotFoundError) as exc:
                scan_form.add_error("scan_barcode", str(exc))
                return render(
                    request,
                    self.template_name,
                    self._build_context(scan_form=scan_form),
                )

            self._attach_unload(unload)
            return redirect("recycling_create")

        unload_id = request.POST.get("unload_id")

        if "reset_unload" in request.POST:
            if unload_id and unload_id.isdigit():
                self._reset_unload(self._get_finished_unload(unload_id))
            return redirect("recycling_create")

        if unload_id and unload_id.isdigit():
            self._attach_unload(self._get_ready_unload(unload_id))
            return redirect("recycling_create")

        new_form = RecyclingForm(request.POST)
        if new_form.is_valid():
            recycling = new_form.save(commit=False)
            BarcodeNumberService.set_barcodes([recycling], prefix=self.BARCODE_PREFIX)
            recycling.status = StatusChoices.AKTIV_IN_ZERLEGUNG
            recycling.save()
            return redirect("recycling_create")

        return render(
            request,
            self.template_name,
            self._build_context(new_form=new_form),
        )
