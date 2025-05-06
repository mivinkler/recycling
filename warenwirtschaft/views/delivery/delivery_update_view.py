from django.views.generic.edit import UpdateView
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.forms import DeliveryUnitFormSet

class DeliveryUpdateView(UpdateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'delivery/delivery_update.html'
    context_object_name = 'delivery'
    success_url = reverse_lazy('delivery_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = DeliveryUnitFormSet(self.request.POST or None, instance=self.object)
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