from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView

from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.models.device_check import DeviceCheck
from warenwirtschaft.forms.device_check_form import DeviceCheckForm


class DeviceCheckSelectView(ListView):
    model = DeviceCheck
    template_name = "device_check/device_check_select.html"
    form_class = DeviceCheckForm
    success_url = reverse_lazy("device_check_select")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unload_list"] = Unload.objects.filter(status=1)
        context["recycling_list"] = Recycling.objects.filter(status=3)
        context["selected_menu"] = "device_check_form"

        return context
