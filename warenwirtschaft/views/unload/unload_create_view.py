from django.views.generic import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction
from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.forms import UnloadFormSet

class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request, *args, **kwargs):
        formset = UnloadFormSet(queryset=Unload.objects.none())
        delivery_units = DeliveryUnit.objects.filter()[:10] # oder .filter(status='activ')
        return render(request, self.template_name, {
            'formset': formset,
            'empty_form': formset.empty_form,
            'delivery_units': delivery_units,
        })

    def post(self, request, *args, **kwargs):
        formset = UnloadFormSet(request.POST)
        delivery_unit_id = request.POST.get('delivery_unit')

        if formset.is_valid() and delivery_unit_id:
            with transaction.atomic():
                delivery_unit = DeliveryUnit.objects.get(id=delivery_unit_id)
                for form in formset:
                    unload = form.save(commit=False)
                    unload.delivery_unit = delivery_unit
                    unload.supplier = delivery_unit.delivery.supplier
                    unload.save()
            return redirect(self.success_url)

        # Im Fehlerfall mit denselben Daten erneut zeigen
        delivery_units = DeliveryUnit.objects.filter(status='activ')
        return render(request, self.template_name, {
            'formset': formset,
            'empty_form': formset.empty_form,
            'delivery_units': delivery_units,
        })
