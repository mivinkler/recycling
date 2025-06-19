from django.views.generic import DetailView
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit

class DeliveryDetailView(DetailView):
    model = Delivery
    template_name = "delivery/delivery_detail.html"
    context_object_name = "delivery"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("units_for_delivery__delivery", "units_for_delivery__material")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["delivery_units"] = self.object.units_for_delivery.all()
        context["box_type"] = DeliveryUnit.BOX_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES
        
        return context

