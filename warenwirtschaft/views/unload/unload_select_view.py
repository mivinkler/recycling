from django.views import View
from django.shortcuts import render

from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadSelectView(View):
    template_name = "unload/unload_select.html"

    def get(self, request):
        delivery_units_ready = DeliveryUnit.objects.filter(
            status=StatusChoices.WARTET_AUF_VORSORTIERUNG,
            is_active=True,
        ).order_by("-pk")

        delivery_units_active = DeliveryUnit.objects.filter(
            status=StatusChoices.IN_VORSORTIERUNG,
            is_active=True,
        ).order_by("-pk")

        return render(
            request,
            self.template_name,
            {
                "delivery_units_ready": delivery_units_ready,
                "delivery_units_active": delivery_units_active,
                "selected_menu": "unload_form",
            },
        )
