from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView

from warenwirtschaft.models.delivery_unit import DeliveryUnit


class DeliveryDeactivateView(UpdateView):
    """
    Bestätigungsseite zum Abschließen einer Entladung:
    - GET  : zeigt Bestätigungsseite
    - POST : setzt Status von 1 -> 4
    """
    model = DeliveryUnit
    template_name = "delivery/delivery_update_status.html"
    context_object_name = "delivery_unit"
    fields = []  # Keine Felder im Form, wir ändern nur den Status
    success_url = reverse_lazy("delivery_list")
    pk_url_kwarg = "delivery_unit_pk"

    def form_valid(self, form):
        delivery = form.instance

        with transaction.atomic():
            delivery.status = 4
            delivery.save(update_fields=["status"])

        messages.success(self.request, "Entladung erfolgreich abgeschlossen.")
        return redirect(self.get_success_url())
