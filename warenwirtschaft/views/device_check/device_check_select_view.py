from django.views.generic import TemplateView
from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.models_common.choices import StatusChoices


class DeviceCheckSelectView(TemplateView):
    template_name = "device_check/device_check_select.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["unload_ready"] = Unload.objects.filter(status=StatusChoices.WARTET_AUF_HALLE_ZWEI)
        context["recycling_ready"] = Recycling.objects.filter(status=StatusChoices.WARTET_AUF_HALLE_ZWEI)

        context["unload_active"] = Unload.objects.filter(status=StatusChoices.IN_HALLE_ZWEI)
        context["recycling_active"] = Recycling.objects.filter(status=StatusChoices.IN_HALLE_ZWEI)

        context["selected_menu"] = "device_check_form"
        return context
