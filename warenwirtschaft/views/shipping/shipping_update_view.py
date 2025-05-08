from django.views.generic.edit import UpdateView
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.models.shipping import Shipping
from warenwirtschaft.forms import ShippingForm
from warenwirtschaft.forms import ShippingUnitFormSet

class ShippingUpdateView(UpdateView):
    model = Shipping
    form_class = ShippingForm
    template_name = 'shipping/shipping_update.html'
    context_object_name = 'shipping'
    success_url = reverse_lazy('shipping_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = ShippingUnitFormSet(self.request.POST or None, instance=self.object)
        context['formset'] = self.formset
        context['empty_form'] = self.formset.empty_form
        return context

    def form_valid(self, form):
        self.get_context_data()
        if self.formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                self.formset.instance = self.object
                self.formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)