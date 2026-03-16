from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models import Recycling, Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService
from warenwirtschaft.services.barcode_scan_service import (
    BarcodeNotFoundError,
    BarcodeScanError,
    BarcodeScanService,
)


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    CREATE_FORM_ID = "recycling-create-form"
    UPDATE_FORM_ID = "recycling-update-form"
    BARCODE_PREFIX = "Z"
    VISIBLE_STATUSES = (
        StatusChoices.AKTIV_IN_ZERLEGUNG,
        StatusChoices.WARTET_AUF_ABHOLUNG,
    )

    def _get_recyclings(self):
        return (
            Recycling.objects.filter(status__in=self.VISIBLE_STATUSES)
            .select_related("material")
            .order_by("pk")
        )

    def _get_recyclings_in_progress(self):
        return Recycling.objects.filter(
            status=StatusChoices.AKTIV_IN_ZERLEGUNG
        ).order_by("pk")

    def _get_unloads_ready(self):
        return (
            Unload.objects.filter(status=StatusChoices.WARTET_AUF_ZERLEGUNG)
            .select_related("material")
            .order_by("pk")
        )

    def _get_unloads_finished_today(self):
        today = timezone.localdate()
        return (
            Unload.objects.filter(
                status=StatusChoices.ERLEDIGT,
                inactive_at__date=today,
            )
            .select_related("material")
            .order_by("-inactive_at", "-pk")
        )

    def _get_context(self, *, new_form=None, edit_recycling=None, form=None, scan_form=None):
        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._get_unloads_ready(),
            "unloads_done_today": self._get_unloads_finished_today(),
            "recyclings": self._get_recyclings(),
            "new_form": new_form or RecyclingForm(form_id=self.CREATE_FORM_ID),
            "edit_recycling": edit_recycling,
            "form": form,
            "scan_form": scan_form or BarcodeScanForm(),
            "create_form_id": self.CREATE_FORM_ID,
            "update_form_id": self.UPDATE_FORM_ID,
        }

    def _render_page(self, request, *, new_form=None, edit_recycling=None, form=None, scan_form=None):
        return render(
            request,
            self.template_name,
            self._get_context(
                new_form=new_form,
                edit_recycling=edit_recycling,
                form=form,
                scan_form=scan_form,
            ),
        )

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

    def _get_unload(self, unload_id, *, status):
        return get_object_or_404(
            Unload,
            pk=int(unload_id),
            status=status,
        )

    def _handle_scan(self, request):
        scan_form = BarcodeScanForm(request.POST)

        try:
            unload = BarcodeScanService.get_unload_for_recycling(
                request.POST.get("scan_barcode")
            )
        except (BarcodeScanError, BarcodeNotFoundError) as exc:
            scan_form.add_error("scan_barcode", str(exc))
            return self._render_page(request, scan_form=scan_form)

        self._attach_unload(unload)
        return redirect("recycling_create")

    def _create_recycling(self, request):
        new_form = RecyclingForm(request.POST, form_id=self.CREATE_FORM_ID)
        if not new_form.is_valid():
            return self._render_page(request, new_form=new_form)

        recycling = new_form.save(commit=False)
        BarcodeNumberService.set_barcodes([recycling], prefix=self.BARCODE_PREFIX)
        recycling.status = StatusChoices.AKTIV_IN_ZERLEGUNG
        recycling.save()
        return redirect("recycling_create")

    def get(self, request):
        return self._render_page(request)

    def post(self, request):
        if request.POST.get("action") == "scan_unload":
            return self._handle_scan(request)

        unload_id = request.POST.get("unload_id")

        if "reset_unload" in request.POST:
            if unload_id and unload_id.isdigit():
                self._reset_unload(
                    self._get_unload(
                        unload_id,
                        status=StatusChoices.ERLEDIGT,
                    )
                )
            return redirect("recycling_create")

        if unload_id and unload_id.isdigit():
            self._attach_unload(
                self._get_unload(
                    unload_id,
                    status=StatusChoices.WARTET_AUF_ZERLEGUNG,
                )
            )
            return redirect("recycling_create")

        return self._create_recycling(request)
