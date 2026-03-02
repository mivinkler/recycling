from django.views.generic import TemplateView
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models_common.choices import StatusChoices


class HalleZweiCreateView(TemplateView):
    template_name = "halle_zwei/halle_zwei_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["delivery_unit_ready"] = DeliveryUnit.objects.filter(
            status=StatusChoices.WARTET_AUF_HALLE_ZWEI
        ).order_by("pk")

        context["halle_zwei_menu"] = "halle_zwei_form"

        return context