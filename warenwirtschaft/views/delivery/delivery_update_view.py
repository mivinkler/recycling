from django.views.generic.edit import UpdateView
from warenwirtschaft.views.delivery.delivery_form_mixin import DeliveryFormMixin


class DeliveryUpdateView(DeliveryFormMixin, UpdateView):
    template_name = "delivery/delivery_update.html"

    extra_units = 0
    generate_barcodes = False