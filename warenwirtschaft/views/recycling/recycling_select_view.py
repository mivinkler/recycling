# warenwirtschaft/views/recycling/recycling_select_view.py
# -*- coding: utf-8 -*-
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from warenwirtschaft.models import Unload
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingSelectView(View):
    """
    Auswahlseite für Unloads, die in die Aufbereitung gehen.
    - AUFBEREITUNG_AUSSTEHEND  -> Weiterleitung zu recycling_create
    - AUFBEREITUNG_LAUFEND     -> Weiterleitung zu recycling_update
    """

    template_name = "recycling/recycling_select.html"

    ALLOWED_STATUSES = {
        StatusChoices.AUFBEREITUNG_AUSSTEHEND,
        StatusChoices.AUFBEREITUNG_LAUFEND,
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
        })

    def post(self, request):
        pk_raw = request.POST.get("unload_id", "")
        if not pk_raw.isdigit():
            return redirect("recycling_select")

        unload = get_object_or_404(Unload, pk=int(pk_raw))

        if unload.status == StatusChoices.AUFBEREITUNG_AUSSTEHEND:
            # wichtig: unload_pk, nicht pk
            return redirect("recycling_create", unload_pk=unload.pk)

        if unload.status == StatusChoices.AUFBEREITUNG_LAUFEND:
            return redirect("recycling_update", pk=unload.pk)

        # falls Status inzwischen nicht mehr passt
        return redirect("recycling_select")
