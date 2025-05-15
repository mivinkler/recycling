from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models.delivery import Delivery

class DeliveryDeleteView(DeleteView):
    model = Delivery
    template_name = 'delivery/delivery_delete.html'
    context_object_name = 'delivery'
    success_url = reverse_lazy('delivery_list')