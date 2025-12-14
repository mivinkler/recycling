# warenwirtschaft/views/recycling/recycling_select_view.py
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from warenwirtschaft.models import Unload
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingSelectView(View):
    """
    Auswahlseite für Unloads, die in die Aufbereitung gehen.
    - AUFBEREITUNG_AUSSTEHEND  -> Weiterleitung zu recycling_create
    - IN_AUFBEREITUNG     -> Weiterleitung zu recycling_update
    """

    template_name = "recycling/recycling_select.html"

    ALLOWED_STATUSES = {
        StatusChoices.WARTET_AUF_AUFBEREITUNG,
        StatusChoices.IN_AUFBEREITUNG,
    }

    def get(self, request):
        unloads = (
            Unload.objects
            .filter(is_active=True, status__in=self.ALLOWED_STATUSES)
            .order_by("created_at")
        )

        return render(request, self.template_name, {
            "unloads": unloads,
            "selected_menu": "recycling_form",
            'status_choices': StatusChoices,
        })

    def post(self, request):
        pk_raw = request.POST.get("unload_id", "")
        if not pk_raw.isdigit():
            return redirect("recycling_select")

        unload = get_object_or_404(Unload, pk=int(pk_raw))

        return redirect("recycling_create", unload_pk=unload.pk)
