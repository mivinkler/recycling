from django.views.generic import DetailView
from warenwirtschaft.models import Shipping

class ShippingDetailView(DetailView):
    model = Shipping
    template_name = 'shipping/shipping_detail.html'
    context_object_name = 'shipping'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["transport"] = Shipping.TRANSPORT_CHOICES

        return context

