# warenwirtschaft/views/unload/unload_update_view.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.unload_form import UnloadForm
from warenwirtschaft.models import DeliveryUnit, Unload


class UnloadUpdateView(View):
    template_name = "unload/unload_update.html"

    # --------------------------------------------------
    # Hilfsmethoden
    # --------------------------------------------------

    def _get_delivery_unit(self, delivery_unit_pk):
        return get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

    def _get_unloads(self, delivery_unit):
        return Unload.objects.filter(
            delivery_units=delivery_unit,
            is_active=True,
        ).order_by("pk")

    def _get_unload(self, delivery_unit, unload_pk):
        return get_object_or_404(
            Unload,
            pk=unload_pk,
            delivery_units=delivery_unit,
            is_active=True,
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
        unloads = self._get_unloads(delivery_unit)
        unload = self._get_unload(delivery_unit, unload_pk)

        form = UnloadForm(request.POST, instance=unload)

        if form.is_valid():
            form.save()
            return redirect(
                reverse("unload_create", kwargs={"delivery_unit_pk": delivery_unit.pk})
            )

        return render(
            request,
            self.template_name,
            {
                "delivery_unit": delivery_unit,
                "unloads": unloads,
                "edit_unload": unload,
                "form": form,
            },
        )