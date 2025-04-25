from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction

from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.forms import UnloadFormSet


class UnloadUpdateView(View):
    template_name = "unload/unload_update.html"
    success_url = reverse_lazy("unload_list")

    def get_delivery_unit(self, pk):
        return get_object_or_404(DeliveryUnit, pk=pk)

    def get(self, request, pk, *args, **kwargs):
        delivery_unit = self.get_delivery_unit(pk)
        formset = UnloadFormSet(instance=delivery_unit)
        return self.render_formset(request, delivery_unit, formset)

    def post(self, request, pk, *args, **kwargs):
        delivery_unit = self.get_delivery_unit(pk)
        formset = UnloadFormSet(request.POST, instance=delivery_unit)

        if formset.is_valid():
            with transaction.atomic():
                for unload in formset.save(commit=False):
                    if not unload.pk:
                        unload.supplier = delivery_unit.delivery.supplier
                    unload.save()
                formset.save_m2m()
            return redirect(self.success_url)

        return self.render_formset(request, delivery_unit, formset)

    def render_formset(self, request, delivery_unit, formset):
        return render(request, self.template_name, {
            "delivery_unit": delivery_unit,
            "formset": formset,
            "empty_form": formset.empty_form,
        })
