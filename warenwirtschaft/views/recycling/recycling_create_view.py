from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService
from warenwirtschaft.services.barcode_scan_service import (
    BarcodeNotFoundError,
    BarcodeScanError,
    BarcodeScanService,
)


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    BARCODE_PREFIX = "Z"
    CREATE_FORM_ID = "recycling-create-form"
    UPDATE_FORM_ID = "recycling-update-form"

    def _unloads_ready(self):
        return Unload.objects.filter(
            status=StatusChoices.WARTET_AUF_ZERLEGUNG
        ).order_by("pk")

    def _unloads_done_today(self):
        today = timezone.localdate()
        return Unload.objects.filter(
            status=StatusChoices.ERLEDIGT,
            inactive_at__date=today,
        ).order_by("-inactive_at", "-pk")

    def _recyclings_active(self):
        return Recycling.objects.filter(
            status=StatusChoices.AKTIV_IN_ZERLEGUNG
        ).order_by("pk")

    def _assign_form_id(self, form, form_id):
        if form is None:
            return None

        for field in form.fields.values():
            field.widget.attrs["form"] = form_id

        return form

    def _context(self, *, new_form=None, edit_recycling=None, form=None, scan_form=None):
        new_form = self._assign_form_id(new_form or RecyclingForm(), self.CREATE_FORM_ID)
        form = self._assign_form_id(form, self.UPDATE_FORM_ID)
        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._unloads_ready(),
            "unloads_done_today": self._unloads_done_today(),
            "recyclings": self._recyclings_active(),
            "status_choices_recycling": StatusChoices.CHOICES,
            "new_form": new_form,
            "edit_recycling": edit_recycling,
            "form": form,
            "scan_form": scan_form or BarcodeScanForm(),
            "create_form_id": self.CREATE_FORM_ID,
            "update_form_id": self.UPDATE_FORM_ID,
        }

    def _attach_unload(self, unload):
        for recycling in self._recyclings_active():
            recycling.unloads.add(unload)

        unload.status = StatusChoices.ERLEDIGT
        unload.inactive_at = timezone.now()
        unload.save(update_fields=["status", "inactive_at"])

    def _reset_unload(self, unload):
        unload.status = StatusChoices.WARTET_AUF_ZERLEGUNG
        unload.inactive_at = None
        unload.save(update_fields=["status", "inactive_at"])

    def get(self, request):
        return render(request, self.template_name, self._context())

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
                    self._context(scan_form=scan_form),
                )

            self._attach_unload(unload)
            return redirect("recycling_create")

        if "reset_unload" in request.POST:
            unload_id = request.POST.get("unload_id")
            if unload_id and unload_id.isdigit():
                unload = get_object_or_404(
                    Unload,
                    pk=int(unload_id),
                    status=StatusChoices.ERLEDIGT,
                )
                self._reset_unload(unload)

            return redirect("recycling_create")

        unload_id = request.POST.get("unload_id")
        if unload_id and unload_id.isdigit():
            unload = get_object_or_404(
                Unload,
                pk=int(unload_id),
                status=StatusChoices.WARTET_AUF_ZERLEGUNG,
            )
            self._attach_unload(unload)
            return redirect("recycling_create")

        new_form = RecyclingForm(request.POST)
        if new_form.is_valid():
            new_recycling = new_form.save(commit=False)

            BarcodeNumberService.set_barcodes([new_recycling], prefix=self.BARCODE_PREFIX)

            new_recycling.status = StatusChoices.AKTIV_IN_ZERLEGUNG
            new_recycling.save()
            return redirect("recycling_create")

        return render(
            request,
            self.template_name,
            self._context(new_form=new_form),
        )
