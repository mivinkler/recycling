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
        if self.request.POST:
            # Wenn ein POST-Request vorliegt, laden wir das Formset mit den neuen Daten
            context['formset'] = DeliveryUnitFormSet(self.request.POST, instance=self.object)
        else:
            # Ansonsten laden wir das Formset mit den bestehenden Objektdaten
            context['formset'] = DeliveryUnitFormSet(instance=self.object)
        context['empty_form'] = context['formset'].empty_form
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            # Atomare Transaktion: Sicherstellen, dass sowohl das Formular als auch das Formset gespeichert werden
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))