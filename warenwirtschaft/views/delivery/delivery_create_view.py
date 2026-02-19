from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.delivery_form import DeliveryForm
from warenwirtschaft.models import Delivery
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class DeliveryCreateView(View):
    template_name = "delivery/delivery_create.html"
    BARCODE_PREFIX = "L"

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "form": DeliveryForm(),
            },
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request):
        form = DeliveryForm(request.POST)

        if form.is_valid():
            # 1) Delivery erstellen
            delivery = Delivery.objects.create(
                customer=form.cleaned_data["customer"],
                delivery_receipt=form.cleaned_data.get("delivery_receipt", ""),
            )

            # 2) DeliveryUnit erstellen
            delivery_unit = form.save(commit=False)
            # delivery_unit.is_active = True

            # FK setzen (NOT NULL constraint!)
            delivery_unit.delivery = delivery

            BarcodeNumberService.set_barcodes([delivery_unit], prefix=self.BARCODE_PREFIX)

            delivery_unit.save()

            return redirect(
                reverse("delivery_update", kwargs={
                "delivery_pk": delivery.pk,
                "delivery_unit_pk": delivery_unit.pk
                })
            )

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "delivery_form",
                "form": form,
            },
        )