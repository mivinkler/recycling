from django.views import View

from django.shortcuts import get_object_or_404, render, redirect
from warenwirtschaft.models import Unload
from warenwirtschaft.forms.unload_form import UnloadForm
from warenwirtschaft.models_common.choices import StatusChoices


class HalleZweiUpdateView(View):
    template_name = "halle_zwei_check/halle_zwei_check_update.html"

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request):
        return render(request, self.template_name, {
            "device_check_ready": Unload.objects.filter(status=StatusChoices.WARTET_AUF_HALLE_ZWEI),
            "device_check_active": Unload.objects.filter(status=StatusChoices.AKTIV_IN_HALLE_ZWEI),
            "selected_menu": "device_check_form",
        })
