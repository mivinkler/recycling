from django.views.generic.edit import UpdateView
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.supplier import Supplier


class DeliveryUpdateView(UpdateView):
    model = Delivery
    template_name = 'delivery/delivery_update.html'
    form_class = DeliveryForm
    context_object_name = 'delivery'

    def get_queryset(self):
        return super().get_queryset().prefetch_related("deliveryunits", "supplier", "deliveryunits__material")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["delivery_units"] = self.object.deliveryunits.all()
        context["materials"] = Material.objects.all()
        context["delivery_type"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES
        context["suppliers"] = Supplier.objects.all()
                
        return context
