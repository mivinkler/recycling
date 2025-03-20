from django.views.generic import DetailView
from warenwirtschaft.models import Delivery
from warenwirtschaft.models import DeliveryUnit

class DeliveryDetailView(DetailView):
    model = Delivery
    template_name = "delivery/delivery_detail.html"
    context_object_name = "delivery"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("deliveryunits", "deliveryunits__material")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["delivery_units"] = self.object.deliveryunits.all()
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["delivery_type"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES
        
        return context

