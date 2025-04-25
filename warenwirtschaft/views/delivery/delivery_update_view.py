from django.views.generic.edit import UpdateView
from warenwirtschaft.models.delivery import Delivery
from django.db import transaction
from warenwirtschaft.forms import DeliveryForm, DeliveryUnitFormSet
from django.urls import reverse_lazy


class DeliveryUpdateView(UpdateView):
    model = Delivery
    template_name = 'delivery/delivery_update.html'
    form_class = DeliveryForm
    context_object_name = 'delivery'
    success_url = reverse_lazy('delivery_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = DeliveryUnitFormSet(self.request.POST or None, instance=self.object)
        context['formset'] = self.formset
        context['empty_form'] = self.formset.empty_form
        return context

    def form_valid(self, form):
        self.get_context_data()  # Zur Initialisierung self.formset
        if self.formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                self.formset.instance = self.object
                self.formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)