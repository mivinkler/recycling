from django.views import View
from django.shortcuts import render

from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadSelectView(View):
    template_name = "unload/unload_select.html"

    def get(self, request):
        return render(request, self.template_name, {
            "delivery_units_ready": DeliveryUnit.objects.filter(status=StatusChoices.WARTET_AUF_VORSORTIERUNG, is_active=True),
            "delivery_units_active": DeliveryUnit.objects.filter(status=StatusChoices.IN_VORSORTIERUNG, is_active=True),
            "selected_menu": "unload_form",
        })
