# warenwirtschaft/views/delivery/delivery_update_view.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.delivery_form import DeliveryForm
from warenwirtschaft.models import Delivery, DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices


class DeliveryUpdateView(View):
    template_name = "delivery/delivery_update.html"

    # --------------------------------------------------
    # Hilfsmethoden
    # --------------------------------------------------

    def _get_delivery(self, delivery_pk):
        return get_object_or_404(Delivery, pk=delivery_pk)

    def _get_delivery_units(self, delivery):
        return DeliveryUnit.objects.filter(delivery=delivery).order_by("pk")

    def _get_delivery_unit(self, delivery, delivery_unit_pk):
        return get_object_or_404(
            DeliveryUnit, 
            pk=delivery_unit_pk, 
            delivery=delivery, 
            status=StatusChoices.AKTIV_IN_VORSORTIERUNG
            )

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, delivery_pk, delivery_unit_pk):
        delivery = self._get_delivery(delivery_pk)
        delivery_units = self._get_delivery_units(delivery)
        delivery_unit = self._get_delivery_unit(delivery, delivery_unit_pk)

        form = DeliveryForm(instance=delivery_unit)

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "delivery": delivery,
                "delivery_units": delivery_units,
                "edit_delivery_unit": delivery_unit,
                "form": form,
            },
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, delivery_pk, delivery_unit_pk):
        delivery = self._get_delivery(delivery_pk)
        delivery_units = self._get_delivery_units(delivery)
        delivery_unit = self._get_delivery_unit(delivery, delivery_unit_pk)

        form = DeliveryForm(request.POST, instance=delivery_unit)

        if form.is_valid():
            form.save()
            return redirect(
                reverse(
                    "warenwirtschaft:delivery_update",
                    kwargs={"delivery_pk": delivery.pk, "delivery_unit_pk": delivery_unit.pk},
                )
            )

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "delivery": delivery,
                "delivery_units": delivery_units,
                "edit_delivery_unit": delivery_unit,
                "form": form,
            },
        )