from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.contrib import messages

from warenwirtschaft.forms.shipping_form import ShippingHeaderForm
from warenwirtschaft.models import Shipping, Recycling, Unload, HalleZwei
from warenwirtschaft.models_common.choices import StatusChoices


class ShippingCreateView(View):
    template_name = "shipping/shipping_create.html"

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _recyclings_ready(self):
        """Recyclings, die auf Abholung warten."""
        return Recycling.objects.filter(
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            shipping__isnull=True,
        ).order_by("pk")

    def _unloads_ready(self):
        """Unloads, die auf Abholung warten."""
        return Unload.objects.filter(
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            shipping__isnull=True,
        ).order_by("pk")

    def _halle_zwei_ready(self):
        """HalleZwei-Einheiten, die auf Abholung warten."""
        return HalleZwei.objects.filter(
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            shipping__isnull=True,
        ).order_by("pk")

    def _context(self, *, form, pre_rec=None, pre_unl=None, pre_hz=None):
        """Gemeinsamer Template-Kontext."""
        return {
            "selected_menu": "shipping_create",
            "form": form,
            "recyclings": self._recyclings_ready(),
            "unloads": self._unloads_ready(),
            "halle_zwei_units": self._halle_zwei_ready(),
            "preselected_recycling_ids": pre_rec or set(),
            "preselected_unload_ids": pre_unl or set(),
            "preselected_halle_zwei_ids": pre_hz or set(),
        }

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request):
        return render(request, self.template_name, self._context(form=ShippingHeaderForm()))

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request):
        form = ShippingHeaderForm(request.POST)

        # IDs aus Checkboxen lesen
        rec_ids = [int(x) for x in request.POST.getlist("selected_recycling") if x.isdigit()]
        unl_ids = [int(x) for x in request.POST.getlist("selected_unload") if x.isdigit()]
        hz_ids = [int(x) for x in request.POST.getlist("selected_halle_zwei") if x.isdigit()]

        # Wenn Fehler: Seite mit markierten Checkboxen neu anzeigen
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                self._context(
                    form=form,
                    pre_rec=set(rec_ids),
                    pre_unl=set(unl_ids),
                    pre_hz=set(hz_ids),
                ),
            )

        # Speichern + Zuordnen
        with transaction.atomic():
            shipping = form.save()

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

        messages.success(request, "Daten wurden gespeichert.")
        return redirect("shipping_create")