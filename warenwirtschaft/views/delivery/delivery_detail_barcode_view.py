from django.views.generic import DetailView
from warenwirtschaft.models.delivery_unit import DeliveryUnit

class DeliveryDetailBarcodeView(DetailView):
    model = DeliveryUnit
    template_name = "delivery/delivery_detail_barcode.html"
    context_object_name = "delivery_unit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        delivery = self.object.delivery

        context["delivery"] = delivery
        context["box_type"] = DeliveryUnit.BOX_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES

        return context


