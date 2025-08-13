# 🇩🇪 Views für Shipping: Kopf + Auswahl vorhandener Recycling-Einheiten (FK auf Recycling.shipping)
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.urls import reverse

from warenwirtschaft.models import Shipping, Recycling
from warenwirtschaft.forms_neu.shipping_form import ShippingHeaderForm

# 🇩🇪 Konstante für die Auswahl der Recycling-Einträge (Abholung)
TARGET_FOR_SHIPPING = 3  # ggf. anpassen, falls in deinem System ein anderer Code für "Abholung" gilt

class ShippingCreateView(View):
    template_name = "shipping/shipping_create.html"

    # 🇩🇪 Hilfsfunktion: passender QuerySet für auswählbare Recycling-Einträge
    def _recycling_queryset(self):
        # 🇩🇪 Zeige nur Einträge mit passendem Target und ohne bereits gesetzten Shipping-FK
        return Recycling.objects.filter(target=TARGET_FOR_SHIPPING, shipping__isnull=True)

    def get(self, request):
        form = ShippingHeaderForm()
        recyclings = self._recycling_queryset()
        # 🇩🇪 beim Erstellen gibt es noch kein Shipping → keine vorausgewählten Checkboxen
        preselected_ids = set()
        return render(request, self.template_name, {
            "form": form,
            "recyclings": recyclings,
            "preselected_ids": preselected_ids,
            "mode": "create",
        })

    def post(self, request):
        form = ShippingHeaderForm(request.POST)
        selected_ids = set(map(int, request.POST.getlist("selected_recycling")))

        if not form.is_valid():
            # 🇩🇪 Fehler im Kopf – Seite mit Fehlern erneut rendern
            return render(request, self.template_name, {
                "form": form,
                "recyclings": self._recycling_queryset(),
                "preselected_ids": selected_ids,
                "mode": "create",
            })

        with transaction.atomic():
            shipping = form.save()  # 🇩🇪 neuen Shipping-Kopf anlegen

            # 🇩🇪 Nur solche Recycling verknüpfen, die wählbar sind (Sicherheit gegen Fremd-IDs)
            allowed_ids = set(self._recycling_queryset().values_list("id", flat=True))
            attach_ids = list(selected_ids & allowed_ids)

            # 🇩🇪 FK setzen (Batch-Update)
            if attach_ids:
                Recycling.objects.filter(pk__in=attach_ids).update(shipping=shipping)

        return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))


class ShippingUpdateView(View):
    template_name = "shipping/shipping_form.html"

    def _recycling_queryset(self, shipping):
        # 🇩🇪 Für Update: zeige solche Recycling,
        #  - die noch frei sind (shipping__isnull=True) ODER
        #  - bereits zu diesem Shipping gehören
        return Recycling.objects.filter(
            target=TARGET_FOR_SHIPPING
        ).filter(
            models.Q(shipping__isnull=True) | models.Q(shipping=shipping)
        )

    def get(self, request, pk):
        shipping = get_object_or_404(Shipping, pk=pk)
        form = ShippingHeaderForm(instance=shipping)
        recyclings = self._recycling_queryset(shipping)
        preselected_ids = set(recyclings.filter(shipping=shipping).values_list("id", flat=True))
        return render(request, self.template_name, {
            "form": form,
            "recyclings": recyclings,
            "preselected_ids": preselected_ids,
            "shipping": shipping,
            "mode": "update",
        })

    def post(self, request, pk):
        shipping = get_object_or_404(Shipping, pk=pk)
        form = ShippingHeaderForm(request.POST, instance=shipping)
        selected_ids = set(map(int, request.POST.getlist("selected_recycling")))

        # 🇩🇪 Erlaube nur IDs aus dem aktuellen Anzeigeset (Sicherheitsfilter)
        qs = self._recycling_queryset(shipping)
        allowed_ids = set(qs.values_list("id", flat=True))

        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "recyclings": qs,
                "preselected_ids": selected_ids & allowed_ids,
                "shipping": shipping,
                "mode": "update",
            })

        with transaction.atomic():
            form.save()

            # 🇩🇪 Zielmenge: IDs, die zu diesem Shipping gehören sollen
            target_ids = selected_ids & allowed_ids

            # 🇩🇪 Aktuell verknüpfte IDs
            current_ids = set(Recycling.objects.filter(shipping=shipping).values_list("id", flat=True))

            # 🇩🇪 Zu verknüpfen (add): in target_ids aber nicht aktuell
            add_ids = list(target_ids - current_ids)
            if add_ids:
                Recycling.objects.filter(pk__in=add_ids).update(shipping=shipping)

            # 🇩🇪 Zu lösen (remove): aktuell, aber nicht mehr in target_ids
            remove_ids = list(current_ids - target_ids)
            if remove_ids:
                Recycling.objects.filter(pk__in=remove_ids).update(shipping=None)

        return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))
