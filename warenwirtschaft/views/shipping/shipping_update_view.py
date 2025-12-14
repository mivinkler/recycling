from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.urls import reverse

from warenwirtschaft.models import Shipping, Recycling, Unload
from warenwirtschaft.forms.shipping_form import ShippingHeaderForm


class ShippingUpdateView(View):
    template_name = "shipping/shipping_update.html"

    # Abhol-bereite QuerySets (Status=3, noch keiner Abholung zugeordnet)
    def _available_recycling_qs(self):
        return Recycling.objects.filter(status=3, shipping__isnull=True)

    def _available_unload_qs(self):
        return Unload.objects.filter(status=3, shipping__isnull=True)

    def get(self, request, pk):
        # Abholung laden
        shipping = get_object_or_404(Shipping, pk=pk)

        # Bereits zugeordnete Einheiten zu dieser Abholung
        attached_recyclings = Recycling.objects.filter(shipping=shipping)
        attached_unloads = Unload.objects.filter(shipping=shipping)

        # Auswahlmenge = verfügbare + bereits zugeordnete (damit Abwahl möglich bleibt)
        recyclings = list(self._available_recycling_qs()) + list(attached_recyclings)
        unloads = list(self._available_unload_qs()) + list(attached_unloads)

        # Vorbelegung für Checkboxen
        preselected_recycling_ids = set(attached_recyclings.values_list("id", flat=True))
        preselected_unload_ids = set(attached_unloads.values_list("id", flat=True))

        form = ShippingHeaderForm(instance=shipping)

        return render(request, self.template_name, {
            "shipping": shipping,
            "form": form,
            "recyclings": recyclings,
            "unloads": unloads,
            "preselected_recycling_ids": preselected_recycling_ids,
            "preselected_unload_ids": preselected_unload_ids,
        })

    def post(self, request, pk):
        shipping = get_object_or_404(Shipping, pk=pk)

        # Eingehende Auswahl (Checkboxen)
        selected_recycling_ids = set(map(int, request.POST.getlist("selected_recycling")))
        selected_unload_ids = set(map(int, request.POST.getlist("selected_unload")))

        form = ShippingHeaderForm(request.POST, instance=shipping)

        # Wiederaufbau der Anzeige-Daten bei Formularfehlern
        attached_recyclings = Recycling.objects.filter(shipping=shipping)
        attached_unloads = Unload.objects.filter(shipping=shipping)
        recyclings = list(self._available_recycling_qs()) + list(attached_recyclings)
        unloads = list(self._available_unload_qs()) + list(attached_unloads)

        if not form.is_valid():
            return render(request, self.template_name, {
                "shipping": shipping,
                "form": form,
                "recyclings": recyclings,
                "unloads": unloads,
                "preselected_recycling_ids": selected_recycling_ids,
                "preselected_unload_ids": selected_unload_ids,
            })

        with transaction.atomic():
            # Kopf speichern
            form.save()

            # Erlaubte IDs: nur aus der Auswahlmenge (verfügbar + bereits angehängt)
            allowed_rec_ids = set([r.id for r in recyclings])
            allowed_unl_ids = set([u.id for u in unloads])

            selected_rec_ids = selected_recycling_ids & allowed_rec_ids
            selected_unl_ids = selected_unload_ids & allowed_unl_ids

            # Aktueller Stand (bereits angehängt)
            current_rec_ids = set(attached_recyclings.values_list("id", flat=True))
            current_unl_ids = set(attached_unloads.values_list("id", flat=True))

            # Delta berechnen
            rec_to_attach = list(selected_rec_ids - current_rec_ids)
            rec_to_detach = list(current_rec_ids - selected_rec_ids)

            unl_to_attach = list(selected_unl_ids - current_unl_ids)
            unl_to_detach = list(current_unl_ids - selected_unl_ids)

            # Anhängen → Abholung setzen, Status=4 (Erledigt)
            if rec_to_attach:
                Recycling.objects.filter(pk__in=rec_to_attach).update(shipping=shipping, status=4)
            if unl_to_attach:
                Unload.objects.filter(pk__in=unl_to_attach).update(shipping=shipping, status=4)

            # Lösen → Abholung entfernen, Status zurück auf 3 (abholbereit)
            if rec_to_detach:
                Recycling.objects.filter(pk__in=rec_to_detach, shipping=shipping).update(shipping=None, status=3)
            if unl_to_detach:
                Unload.objects.filter(pk__in=unl_to_detach, shipping=shipping).update(shipping=None, status=3)

        return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))
