from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from warenwirtschaft.models import DeliveryUnit, Device, unload
from warenwirtschaft.forms import unloadFormSet


class unloadCreateView(TemplateView):
    template_name = "unload/unload_create.html"
    success_url = reverse_lazy('unload_create')

    def get_context_data(self, **kwargs):
        formset = unloadFormSet(queryset=unload.objects.none())
        devices = Device.objects.all()

        return {
            **super().get_context_data(**kwargs),
            'page_obj': self.get_paginated_units(),
            'formset': formset,
            'devices': devices,
        }

    def get_paginated_units(self):
        return Paginator(
            DeliveryUnit.objects.filter(status=1).order_by('id'), 6
        ).get_page(self.request.GET.get("page", 1))

    def post(self, request):
        delivery_unit = get_object_or_404(DeliveryUnit, id=request.POST.get("delivery_unit"))
        
        formset = unloadFormSet(request.POST)

        if formset.is_valid():
            unloads = formset.save(commit=False)

            for unload in unloads:
                unload.delivery_unit = delivery_unit
                unload.supplier = delivery_unit.delivery.supplier
                unload.save()

            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(formset=formset))