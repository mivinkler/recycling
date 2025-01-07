from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from warenwirtschaft.models import Delivery
from warenwirtschaft.forms import DeliveryForm


class DeliveryCreateView(CreateView):
    model = Delivery
    template_name = "delivery/delivery_create.html"
    form_class = DeliveryForm

    def get_success_url(self):
        return reverse_lazy("delivery_create")
