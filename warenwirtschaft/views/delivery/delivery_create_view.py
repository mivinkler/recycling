import uuid
from django.views.generic.edit import CreateView
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.forms import DeliveryForm, DeliveryUnitFormSet
from warenwirtschaft.services.barcode_service import BarcodeGenerator

class DeliveryCreateView(CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'delivery/delivery_create.html'
    context_object_name = 'delivery'
    success_url = reverse_lazy('delivery_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DeliveryUnitFormSet(self.request.POST)
        else:
            context['formset'] = DeliveryUnitFormSet()
        context['empty_form'] = context['formset'].empty_form
        context["selected_menu"] = "delivery_create"
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                units = formset.save(commit=False)

                for unit in units:
                    suffix = uuid.uuid4().hex[:8].upper()
                    code = f"L{suffix}"
                    unit.barcode = code
                    BarcodeGenerator(unit, code, 'barcodes/delivery').generate_image()
                    unit.save()

            return super().form_valid(form)

        return self.render_to_response(self.get_context_data(form=form))
