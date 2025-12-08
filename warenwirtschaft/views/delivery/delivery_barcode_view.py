from django.views.generic import DetailView
from warenwirtschaft.models.delivery_unit import DeliveryUnit

class DeliveryBarcodeView(DetailView):
    model = DeliveryUnit
    template_name = "delivery/delivery_barcode.html"
    context_object_name = "delivery_unit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        delivery = self.object.delivery

        context["delivery"] = delivery
        context["box_type"] = DeliveryUnit.box_type

        return context


