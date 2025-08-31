from django.views.generic import DetailView
from warenwirtschaft.models.shipping import Shipping

class ShippingDetailView(DetailView):
    model = Shipping
    template_name = "shipping/shipping_detail.html"
    context_object_name = "shipping"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("units_for_shipping", "units_for_shipping__material")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["shipping_units"] = self.object.units_for_shipping.all()
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        
        return context
