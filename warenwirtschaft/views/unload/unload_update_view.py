# warenwirtschaft/views/unload/unload_update_view.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.unload_form import UnloadForm
from warenwirtschaft.models import DeliveryUnit, Unload
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadUpdateView(View):
    template_name = "unload/unload_update.html"

    # --------------------------------------------------
    # Hilfsmethoden
    # --------------------------------------------------

    def _get_delivery_unit(self, delivery_unit_pk):
        return get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

    def _get_unloads(self, delivery_unit):
        return (
            Unload.objects.filter(delivery_units=delivery_unit)
            .exclude(status=StatusChoices.ERLEDIGT)
            .order_by("pk")
        )

    def _get_unload(self, delivery_unit, unload_pk):
        return get_object_or_404(
            Unload.objects.filter(delivery_units=delivery_unit)
            .exclude(status=StatusChoices.ERLEDIGT),
            pk=unload_pk,
        )

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, delivery_unit_pk, unload_pk):
        delivery_unit = self._get_delivery_unit(delivery_unit_pk)
        unloads = self._get_unloads(delivery_unit)
        unload = self._get_unload(delivery_unit, unload_pk)

        form = UnloadForm(instance=unload)

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "unload_form",
                "delivery_unit": delivery_unit,
                "unloads": unloads,
                "edit_unload": unload,
                "form": form,
            },
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, delivery_unit_pk, unload_pk):
        delivery_unit = self._get_delivery_unit(delivery_unit_pk)
        unload = self._get_unload(delivery_unit, unload_pk)

        if "finish_unload" in request.POST:
            return self.finish_unload(request, delivery_unit)

        if "save_unload" in request.POST:
            return self.save_unload(request, delivery_unit, unload)

        return redirect(
            "unload_update",
            delivery_unit_pk=delivery_unit.pk,
            unload_pk=unload.pk,
        )

    # --------------------------------------------------
    # Aktionen
    # --------------------------------------------------

    def save_unload(self, request, delivery_unit, unload):
        form = UnloadForm(request.POST, instance=unload)

        if form.is_valid():
            form.save()

            return redirect(
                reverse(
                    "unload_create",
                    kwargs={"delivery_unit_pk": delivery_unit.pk},
                )
            )

        unloads = self._get_unloads(delivery_unit)

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "unload_form",
                "delivery_unit": delivery_unit,
                "unloads": unloads,
                "edit_unload": unload,
                "form": form,
            },
        )

    def finish_unload(self, request, delivery_unit):
        # Status der Liefereinheit auf erledigt setzen
        delivery_unit.status = StatusChoices.ERLEDIGT
        delivery_unit.save(update_fields=["status"])

        return redirect("unload_select")