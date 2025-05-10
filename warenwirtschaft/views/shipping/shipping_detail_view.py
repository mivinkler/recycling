from django.views.generic import DetailView
from warenwirtschaft.models.shipping import Shipping
from warenwirtschaft.models.shipping_unit import ShippingUnit

class ShippingDetailView(DetailView):
    model = Shipping
    template_name = "shipping/shipping_detail.html"
    context_object_name = "shipping"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("shipping", "material")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["shipping_units"] = self.object.shippingunits.all()
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["box_type"] = ShippingUnit.BOX_TYPE_CHOICES
        context["statuses"] = ShippingUnit.STATUS_CHOICES
        
        return context

