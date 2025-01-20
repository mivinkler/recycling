from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from warenwirtschaft.models import DeliveryUnits, Device, Unloading
from warenwirtschaft.forms import UnloadingFormSet


class UnloadingCreateView(TemplateView):
    template_name = "unloading/unloading_create.html"
    success_url = reverse_lazy('unloading_create')

    def get_context_data(self, **kwargs):
        formset = UnloadingFormSet(queryset=Unloading.objects.none())
        devices = Device.objects.all()

        return {
            **super().get_context_data(**kwargs),
            'page_obj': self.get_paginated_units(),
            'formset': formset,
            'devices': devices,
        }

    def get_paginated_units(self):
        return Paginator(
            DeliveryUnits.objects.filter(status=1).order_by('id'), 6
        ).get_page(self.request.GET.get("page", 1))

    def post(self, request):
        delivery_unit = get_object_or_404(DeliveryUnits, id=request.POST.get("delivery_unit"))
        
        formset = UnloadingFormSet(request.POST)
        
        if formset.is_valid():
            unloadings = formset.save(commit=False)
            for unloading in unloadings:
                unloading.delivery_unit = delivery_unit
                unloading.supplier = delivery_unit.delivery.supplier
                unloading.save()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))