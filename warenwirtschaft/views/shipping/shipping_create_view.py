# Views für Shipping: Kopf + Auswahl vorhandener Recycling-Einheiten (FK auf Recycling.shipping)
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.urls import reverse

from warenwirtschaft.models import Shipping, Recycling, Unload
from warenwirtschaft.forms_neu.shipping_form import ShippingHeaderForm



class ShippingCreateView(View):
    template_name = "shipping/shipping_create.html"

    # Hilfsfunktion: QuerySet für auswählbare Recyclings
    def _recycling_queryset(self):
        # Einträge nur mit target "Abholung"
        return Recycling.objects.filter(target=3)
    
    # Hilfsfunktion: QuerySet für auswählbare Unloads
    def _unload_queryset(self):
        # Einträge nur mit target "Abholung"
        return Unload.objects.filter(target=3)

    def get(self, request):
        return render(request, self.template_name, {
            "form": ShippingHeaderForm(),
            "recyclings": self._recycling_queryset(),
            "unloads": self._unload_queryset(),
            "preselected_ids": set(),
        })

    def post(self, request):
        form = ShippingHeaderForm(request.POST)
        selected_ids = set(map(int, request.POST.getlist("selected_recycling")))

        if not form.is_valid():
            # Fehler im Itemcard-Header – Seite mit Fehlern erneut rendern
            return render(request, self.template_name, {
                "form": form,
                "recyclings": self._recycling_queryset(),
                "preselected_ids": selected_ids,
            })

        with transaction.atomic():
            shipping = form.save()  # neuen Shipping-Kopf anlegen

            # Nur solche Recycling verknüpfen, die wählbar sind (Sicherheit gegen Fremd-IDs)
            allowed_ids = set(self._recycling_queryset().values_list("id", flat=True))
            attach_ids = list(selected_ids & allowed_ids)

            # FK setzen (Batch-Update)
            if attach_ids:
                Recycling.objects.filter(pk__in=attach_ids).update(shipping=shipping)

        return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))