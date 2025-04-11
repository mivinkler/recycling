from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.forms import UnloadFormSet

class UnloadUpdateView(View):
    template_name = 'unload/unload_update.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request, pk, *args, **kwargs):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=pk)
        queryset = Unload.objects.filter(delivery_unit=delivery_unit)
        formset = UnloadFormSet(queryset=queryset)
        return render(request, self.template_name, {
            'formset': formset,
            'empty_form': formset.empty_form,
            'delivery_unit': delivery_unit,
        })

    def post(self, request, pk, *args, **kwargs):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=pk)
        queryset = Unload.objects.filter(delivery_unit=delivery_unit)
        formset = UnloadFormSet(request.POST, queryset=queryset)

        if formset.is_valid():
            with transaction.atomic():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.delivery_unit = delivery_unit
                    instance.supplier = delivery_unit.delivery.supplier
                    instance.save()
                formset.save_m2m()
            return redirect(self.success_url)

        return render(request, self.template_name, {
            'formset': formset,
            'empty_form': formset.empty_form,
            'delivery_unit': delivery_unit,
        })