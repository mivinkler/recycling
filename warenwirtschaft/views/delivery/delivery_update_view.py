from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from warenwirtschaft.models import Delivery
from warenwirtschaft.forms import DeliveryForm


class DeliveryUpdateView(UpdateView):
    model = Delivery
    template_name = 'delivery/delivery_update.html'
    form_class = DeliveryForm
    context_object_name = 'delivery'

    def get_success_url(self):
        return reverse_lazy('delivery_list')
