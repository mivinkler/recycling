# Views für Shipping: Kopf + Auswahl vorhandener Recycling-/Unload-Einheiten
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.urls import reverse
from django.db.models import Q

from warenwirtschaft.models import Shipping, Recycling, Unload
from warenwirtschaft.forms.shipping_form import ShippingHeaderForm


class ShippingCreateView(View):
    template_name = "shipping/shipping_create.html"

    # Abhol-bereite QuerySets (Status=3)
    def _recycling_queryset(self):
        return Recycling.objects.filter(status=3, shipping__isnull=True)

    def _unload_queryset(self):
        return Unload.objects.filter(status=3, shipping__isnull=True)

    def get(self, request):
        return render(request, self.template_name, {
            "form": ShippingHeaderForm(),
            "recyclings": self._recycling_queryset(),
            "unloads": self._unload_queryset(),
            "preselected_recycling_ids": set(),
            "preselected_unload_ids": set(),
            "selected_menu": "shipping_create",
        })

    def post(self, request):
        form = ShippingHeaderForm(request.POST)
        selected_recycling_ids = set(map(int, request.POST.getlist("selected_recycling")))
        selected_unload_ids = set(map(int, request.POST.getlist("selected_unload")))

        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "recyclings": self._recycling_queryset(),
                "unloads": self._unload_queryset(),
                "preselected_recycling_ids": selected_recycling_ids,
                "preselected_unload_ids": selected_unload_ids,
            })

        with transaction.atomic():
            shipping = form.save()

            # Sicherheitsfilter: nur erlaubte IDs aus den QuerySets
            allowed_rec_ids = set(self._recycling_queryset().values_list("id", flat=True))
            allowed_unl_ids = set(self._unload_queryset().values_list("id", flat=True))

            attach_rec_ids = list(selected_recycling_ids & allowed_rec_ids)
            attach_unl_ids = list(selected_unload_ids & allowed_unl_ids)

            if attach_rec_ids:
                Recycling.objects.filter(pk__in=attach_rec_ids).update(
                    shipping=shipping,
                    status=4  # Erledigt
                )

            if attach_unl_ids:
                Unload.objects.filter(pk__in=attach_unl_ids).update(
                    shipping=shipping,
                    status=4  # Erledigt
                )

        return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))

