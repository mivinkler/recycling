from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models.halle_zwei import HalleZwei
from warenwirtschaft.models_common.choices import StatusChoices


class HalleZweiCreateView(View):
    template_name = "halle_zwei/halle_zwei_create.html"

    def get(self, request):
        delivery_units = DeliveryUnit.objects.filter(
            status=StatusChoices.WARTET_AUF_HALLE_ZWEI
        ).order_by("pk")

        today_checked = HalleZwei.objects.filter(
            delivery_unit__status=StatusChoices.WARTET_AUF_ABHOLUNG
        ).select_related("delivery_unit").order_by("-created_at")

        context = {
            "delivery_unit_ready": delivery_units,
            "today_checked": today_checked,
        }

        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request):
        delivery_unit_id = request.POST.get("delivery_unit_id")
        action = request.POST.get("action")

        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_id)

        if action == "check":

            HalleZwei.objects.get_or_create(
                delivery_unit=delivery_unit,
                defaults={
                    "status": StatusChoices.WARTET_AUF_ABHOLUNG,
                    "halle_zwei": True,
                },
            )

            delivery_unit.status = StatusChoices.WARTET_AUF_ABHOLUNG
            delivery_unit.save()

        elif action == "uncheck":

            HalleZwei.objects.filter(delivery_unit=delivery_unit).delete()

            delivery_unit.status = StatusChoices.WARTET_AUF_HALLE_ZWEI
            delivery_unit.save()

        return redirect("halle_zwei_create")