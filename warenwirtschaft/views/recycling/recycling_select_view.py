from django.views import View
from django.shortcuts import render

from warenwirtschaft.models import Unload
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingSelectView(View):
    template_name = "recycling/recycling_select.html"

    def get(self, request):
        return render(request, self.template_name, {
            "unloads_ready": Unload.objects.filter(status=StatusChoices.WARTET_AUF_ZERLEGUNG),
            "unloads_active": Unload.objects.filter(status=StatusChoices.AKTIV_IN_ZERLEGUNG),
            "selected_menu": "recycling_form",
        })