# warenwirtschaft/views/unload/unload_select_view.py
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404

from warenwirtschaft.models import DeliveryUnit


class UnloadSelectView(View):
    template_name = "unload/unload_select.html"

    def get(self, request):
        delivery_units = (
            DeliveryUnit.objects
            .filter(is_active=True)
            .order_by("created_at")
        )

        return render(request, self.template_name, {
            "delivery_units": delivery_units,
            "selected_menu": "unload_form",
        })

    def post(self, request):
        pk_raw = request.POST.get("delivery_unit_id", "")
        if not pk_raw.isdigit():
            return redirect("unload_select")

        delivery_unit = get_object_or_404(DeliveryUnit, pk=int(pk_raw))

        return redirect("unload_create", delivery_unit_pk=delivery_unit.pk)
