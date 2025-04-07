from django.views.generic.edit import UpdateView
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.supplier import Supplier
from warenwirtschaft.forms import DeliveryForm, DeliveryUnitFormSet
from django.urls import reverse_lazy
from django.db import transaction


class DeliveryUpdateView(UpdateView):
    model = Delivery
    template_name = 'delivery/delivery_update.html'
    form_class = DeliveryForm
    context_object_name = 'delivery'
    success_url = reverse_lazy('delivery_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DeliveryUnitFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DeliveryUnitFormSet(instance=self.object)
        
        context["materials"] = Material.objects.all()
        context["suppliers"] = Supplier.objects.all()
        context["statuses"] = DeliveryUnit.STATUS_CHOICES
        context["delivery_type"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["delivery_units"] = self.object.deliveryunits.all()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)