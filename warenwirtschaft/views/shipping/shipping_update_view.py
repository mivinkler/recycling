from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.shipping_form import ShippingHeaderForm
from warenwirtschaft.models import Shipping, Recycling, Unload, HalleZwei
from warenwirtschaft.models_common.choices import StatusChoices


class ShippingUpdateView(View):
    template_name = "shipping/shipping_update.html"

    def get(self, request, pk):
        shipping = get_object_or_404(Shipping, pk=pk)
        form = ShippingHeaderForm(instance=shipping)

        # Bereits zugeordnet (Checkbox = checked)
        attached_recyclings = Recycling.objects.filter(shipping=shipping).order_by("pk")
        attached_unloads = Unload.objects.filter(shipping=shipping).order_by("pk")
        attached_hz = HalleZwei.objects.filter(shipping=shipping).order_by("pk")

        preselected_recycling_ids = set(attached_recyclings.values_list("id", flat=True))
        preselected_unload_ids = set(attached_unloads.values_list("id", flat=True))
        preselected_halle_zwei_ids = set(attached_hz.values_list("id", flat=True))

        # Frei + bereit (Status=7, noch ohne Shipping)
        ready_recyclings = Recycling.objects.filter(
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            shipping__isnull=True,
        ).order_by("pk")

        ready_unloads = Unload.objects.filter(
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            shipping__isnull=True,
        ).order_by("pk")

        ready_hz = HalleZwei.objects.filter(
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            shipping__isnull=True,
        ).order_by("pk")

        # Liste im Template = schon zugeordnet + freie
        recyclings = list(attached_recyclings) + list(ready_recyclings)
        unloads = list(attached_unloads) + list(ready_unloads)
        halle_zwei_units = list(attached_hz) + list(ready_hz)

        return render(request, self.template_name, {
            "selected_menu": "shipping_create",
            "shipping": shipping,
            "form": form,
            "recyclings": recyclings,
            "unloads": unloads,
            "halle_zwei_units": halle_zwei_units,
            "preselected_recycling_ids": preselected_recycling_ids,
            "preselected_unload_ids": preselected_unload_ids,
            "preselected_halle_zwei_ids": preselected_halle_zwei_ids,
        })

    def post(self, request, pk):
        shipping = get_object_or_404(Shipping, pk=pk)
        form = ShippingHeaderForm(request.POST, instance=shipping)

        # IDs aus Checkboxen
        rec_ids = [int(x) for x in request.POST.getlist("selected_recycling") if x.isdigit()]
        unl_ids = [int(x) for x in request.POST.getlist("selected_unload") if x.isdigit()]
        hz_ids = [int(x) for x in request.POST.getlist("selected_halle_zwei") if x.isdigit()]

        if not form.is_valid():
            # Verhindet, dass active Checkboxes aufgrund eines Formularfehlers verschwinden
            attached_rec_ids = set(Recycling.objects.filter(shipping=shipping).values_list("id", flat=True))
            attached_unl_ids = set(Unload.objects.filter(shipping=shipping).values_list("id", flat=True))
            attached_hz_ids = set(HalleZwei.objects.filter(shipping=shipping).values_list("id", flat=True))

            preselected_recycling_ids = attached_rec_ids.copy()
            preselected_recycling_ids.update(rec_ids)

            preselected_unload_ids = attached_unl_ids.copy()
            preselected_unload_ids.update(unl_ids)

            preselected_halle_zwei_ids = attached_hz_ids.copy()
            preselected_halle_zwei_ids.update(hz_ids)

            # Liste = schon zugeordnete + nicht zugeordnete
            attached_recyclings = Recycling.objects.filter(shipping=shipping).order_by("pk")
            attached_unloads = Unload.objects.filter(shipping=shipping).order_by("pk")
            attached_hz = HalleZwei.objects.filter(shipping=shipping).order_by("pk")

            ready_recyclings = Recycling.objects.filter(
                status=StatusChoices.WARTET_AUF_ABHOLUNG,
                shipping__isnull=True,
            ).order_by("pk")

            ready_unloads = Unload.objects.filter(
                status=StatusChoices.WARTET_AUF_ABHOLUNG,
                shipping__isnull=True,
            ).order_by("pk")

            ready_hz = HalleZwei.objects.filter(
                status=StatusChoices.WARTET_AUF_ABHOLUNG,
                shipping__isnull=True,
            ).order_by("pk")

            return render(request, self.template_name, {
                "selected_menu": "shipping_create",
                "shipping": shipping,
                "form": form,
                "recyclings": list(attached_recyclings) + list(ready_recyclings),
                "unloads": list(attached_unloads) + list(ready_unloads),
                "halle_zwei_units": list(attached_hz) + list(ready_hz),
                "preselected_recycling_ids": preselected_recycling_ids,
                "preselected_unload_ids": preselected_unload_ids,
                "preselected_halle_zwei_ids": preselected_halle_zwei_ids,
            })

        with transaction.atomic():
            form.save()

            if rec_ids:
                Recycling.objects.filter(pk__in=rec_ids).update(
                    shipping=shipping,
                    status=StatusChoices.ERLEDIGT,
                )
            if unl_ids:
                Unload.objects.filter(pk__in=unl_ids).update(
                    shipping=shipping,
                    status=StatusChoices.ERLEDIGT,
                )
            if hz_ids:
                HalleZwei.objects.filter(pk__in=hz_ids).update(
                    shipping=shipping,
                    status=StatusChoices.ERLEDIGT,
                )

        return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))