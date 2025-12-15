# warenwirtschaft/views/device_check/device_check_select_view.py
# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from warenwirtschaft.models import Unload, Recycling


class DeviceCheckSelectView(TemplateView):
    template_name = "device_check/device_check_select.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unload_list"] = Unload.objects.filter(status=1)
        context["recycling_list"] = Recycling.objects.filter(status=3)
        context["selected_menu"] = "device_check_form"
        return context
