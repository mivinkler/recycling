from django.views.generic.edit import CreateView
from warenwirtschaft.views.delivery.delivery_form_mixin import DeliveryFormMixin


class DeliveryCreateView(DeliveryFormMixin, CreateView):
    template_name = "delivery/delivery_create.html"

    extra_units = 1
    generate_barcodes = True
