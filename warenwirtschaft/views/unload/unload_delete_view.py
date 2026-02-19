from django.views.generic import DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse

from warenwirtschaft.models import DeliveryUnit, Unload
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadDeleteView(DeleteView):
    model = Unload
    template_name = "unload/unload_delete.html"
    context_object_name = "unload"

    def get_object(self, queryset=None):
        # Nur Unload löschen, der mit DeliveryUnit verknüpft ist
        return get_object_or_404(
            Unload,
            pk=self.kwargs["unload_pk"],
            delivery_units__pk=self.kwargs["delivery_unit_pk"],
            ).exclude(
            status=StatusChoices.ERLEDIGT
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delivery_unit"] = get_object_or_404(
            DeliveryUnit,
            pk=self.kwargs["delivery_unit_pk"],
        )
        return context

    def get_success_url(self):
        return reverse(
            "unload_create",
            kwargs={"delivery_unit_pk": self.kwargs["delivery_unit_pk"]},
        )