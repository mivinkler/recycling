from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from warenwirtschaft.models import Delivery
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.models import Device


class DeliveryCreateView(CreateView):
    model = Delivery
    template_name = "delivery/delivery_create.html"
    form_class = DeliveryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['devices'] = Device.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy("delivery_create")
