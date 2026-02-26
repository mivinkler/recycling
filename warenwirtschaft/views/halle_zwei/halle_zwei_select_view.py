from django.views.generic import View
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices


class HalleZweiSelectView(View):
    template_name = "halle_zwei/halle_zwei_select.html"

    def get(self, **kwargs):
        context = super().get(**kwargs)

        context["halle_zwei_active"] = DeliveryUnit.objects.filter(status=StatusChoices.WARTET_AUF_HALLE_ZWEI)
        context["recycling_active"] = DeliveryUnit.objects.filter(status=StatusChoices.WARTET_AUF_HALLE_ZWEI)

        context["halle_zwei_menu"] = "halle_zwei_form"
        return context
