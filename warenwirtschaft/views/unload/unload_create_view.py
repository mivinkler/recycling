from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
# from django.utils import timezone

from warenwirtschaft.forms.unload_form import UnloadForm
from warenwirtschaft.models import DeliveryUnit, Unload
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadCreateView(View):
    template_name = "unload/unload_create.html"
    BARCODE_PREFIX = "V"

    # --------------------------------------------------
    # Hilfsmethoden
    # --------------------------------------------------

    def _get_delivery_unit(self, delivery_unit_pk):
        return get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

    def _get_unloads(self, delivery_unit):
        return Unload.objects.filter(
            delivery_units=delivery_unit
        ).exclude(
            status=StatusChoices.ERLEDIGT
        ).order_by("pk")

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, delivery_unit_pk):
        delivery_unit = self._get_delivery_unit(delivery_unit_pk)

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "unload_form",
                "delivery_unit": delivery_unit,
                "unloads": self._get_unloads(delivery_unit),
                "form": UnloadForm(),
            },
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, delivery_unit_pk):
        delivery_unit = self._get_delivery_unit(delivery_unit_pk)

        if "finish_unload" in request.POST:
            return self.finish_unload(request, delivery_unit)

        if "save_unload" in request.POST:
            return self.save_unload(request, delivery_unit)

        return redirect("unload_create", delivery_unit_pk=delivery_unit.pk)

    # --------------------------------------------------
    # Aktionen
    # --------------------------------------------------

    def save_unload(self, request, delivery_unit):
        form = UnloadForm(request.POST)

        if form.is_valid():
            unload = form.save(commit=False)

            BarcodeNumberService.set_barcodes([unload], prefix=self.BARCODE_PREFIX)

            unload.save()
            unload.delivery_units.add(delivery_unit)

            # Status setzen
            delivery_unit.status = StatusChoices.AKTIV_IN_VORSORTIERUNG
            delivery_unit.save(update_fields=["status"])

        return redirect("unload_create", delivery_unit_pk=delivery_unit.pk)

    def finish_unload(self, request, delivery_unit):
        # Status der Liefereinheit auf erledigt setzen
        delivery_unit.status = StatusChoices.ERLEDIGT
        # delivery_unit.inactive_at = timezone.now()
        delivery_unit.save(update_fields=["status"])

        return redirect("unload_select")