# warenwirtschaft/views/device_check/device_check_create_view.py
# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView

from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.forms.device_check_form import DeviceCheckForm


class DeviceCheckCreateView(FormView):
    template_name = "device_check/device_check_create.html"
    form_class = DeviceCheckForm

    def get_success_url(self):
        return reverse_lazy("device_check_select")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        source = self.kwargs["source"]
        pk = self.kwargs["pk"]

        if source == "unload":
            kwargs["unload_qs"] = Unload.objects.filter(pk=pk, is_active=True)
            kwargs["recycling_qs"] = Recycling.objects.none()
        else:
            kwargs["unload_qs"] = Unload.objects.none()
            kwargs["recycling_qs"] = Recycling.objects.filter(pk=pk, is_active=True)

        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["container"] = f"{self.kwargs['source']}-{self.kwargs['pk']}"
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        source = self.kwargs["source"]
        pk = self.kwargs["pk"]

        if source == "unload":
            context["source_obj"] = get_object_or_404(Unload, pk=pk)
            context["source_label"] = "Vorsortierung"
        else:
            context["source_obj"] = get_object_or_404(Recycling, pk=pk)
            context["source_label"] = "Aufbereitung"

        return context
