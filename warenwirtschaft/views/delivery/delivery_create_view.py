from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from warenwirtschaft.models import Delivery
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.forms import DeliveryUnitFormSet
from django.db import transaction

class DeliveryCreateView(CreateView):
    model = Delivery
    template_name = 'delivery/delivery_create.html'
    form_class = DeliveryForm
    context_object_name = 'delivery'
    success_url = reverse_lazy('delivery_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DeliveryUnitFormSet(self.request.POST)
        else:
            context['formset'] = DeliveryUnitFormSet()
        context['empty_form'] = context['formset'].empty_form
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
        return self.render_to_response(self.get_context_data(form=form))