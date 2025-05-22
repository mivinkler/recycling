from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models import Shipping

class ShippingDeleteView(DeleteView):
    model = Shipping
    template_name = 'shipping/shipping_delete.html'
    context_object_name = 'shipping'
    success_url = reverse_lazy('shipping_list')