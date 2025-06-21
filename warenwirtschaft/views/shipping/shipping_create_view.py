from django.views.generic.edit import CreateView
from django.db import transaction
from django.urls import reverse_lazy
from warenwirtschaft.models.shipping import Shipping
from warenwirtschaft.forms import ShippingForm, ShippingUnitFormSet

class ShippingCreateView(CreateView):
    model = Shipping
    form_class = ShippingForm
    template_name = 'shipping/shipping_create.html'
    context_object_name = 'shipping'
    success_url = reverse_lazy('shipping_units_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = ShippingUnitFormSet(self.request.POST or None)
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

        print("❌ Formset errors:", formset.errors)
        return self.render_to_response(self.get_context_data(form=form))
