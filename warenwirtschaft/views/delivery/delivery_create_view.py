from django.db import transaction
from django.shortcuts import redirect
from django.views.generic.edit import CreateView

from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.forms.delivery_form import DeliveryForm
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService
from warenwirtschaft.views.delivery.delivery_form_mixin import DeliveryFormMixin


class DeliveryCreateView(DeliveryFormMixin, CreateView):
    template_name = "delivery/delivery_create.html"

    model = Delivery
    form_class = DeliveryForm
    context_object_name = "delivery"

    extra_units = 1
    BARCODE_PREFIX = "L"

    def form_valid(self, form):
        # Formset validieren
        self.formset = self.get_units_formset()
        if not self.formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            # 1) Lieferung speichern
            self.object = form.save()
            self.formset.instance = self.object

            # 2) Units holen (noch nicht speichern)
            units = self.formset.save(commit=False)

            # 3) Create-spezifisch: Barcodes erzeugen
            BarcodeNumberService.set_barcodes(units, prefix=self.BARCODE_PREFIX)

            # 4) Units speichern
            for unit in units:
                unit.save()

            # 5) M2M speichern (falls vorhanden)
            if hasattr(self.formset, "save_m2m"):
                self.formset.save_m2m()

        # Nach Create auf Update umleiten
        return redirect("delivery_update", pk=self.object.pk)
