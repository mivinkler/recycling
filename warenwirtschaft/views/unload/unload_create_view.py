# warenwirtschaft/views/unload/unload_create_view.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.unload_form import UnloadForm
from warenwirtschaft.models import DeliveryUnit, Unload
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadCreateView(View):
    template_name = "unload/unload_create.html"
    BARCODE_PREFIX = "S"

    # --------------------------------------------------
    # Hilfsmethoden
    # --------------------------------------------------

    def _get_delivery_unit(self, delivery_unit_pk):
        return get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

    def _get_unloads(self, delivery_unit):
        return Unload.objects.filter(
            delivery_units=delivery_unit,
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
        form = UnloadForm(request.POST)

        if form.is_valid():
            unload = form.save(commit=False)

            BarcodeNumberService.set_barcodes([unload], prefix=self.BARCODE_PREFIX)

            unload.save()
            unload.delivery_units.add(delivery_unit)

            return redirect(reverse("unload_create", kwargs={"delivery_unit_pk": delivery_unit.pk}))

        return render(
            request,
            self.template_name,
            {
                "delivery_unit": delivery_unit,
                "unloads": self._get_unloads(delivery_unit),
                "form": form,
            },
        )