from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.forms.shipping_form import ShippingHeaderForm
from warenwirtschaft.models import HalleZwei, Recycling, Shipping, Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_scan_service import (
    BarcodeNotFoundError,
    BarcodeScanError,
    BarcodeScanService,
)


class ShippingUpdateView(View):
    template_name = "shipping/shipping_update.html"
    GENERATED_FIELD_MAP = {
        "customer": "customer_id",
        "certificate": "certificate",
        "transport": "transport",
    }

    def _attached_recyclings(self, shipping):
        return Recycling.objects.filter(shipping=shipping).select_related("material").order_by("pk")

    def _attached_unloads(self, shipping):
        return Unload.objects.filter(shipping=shipping).select_related("material").order_by("pk")

    def _attached_halle_zwei(self, shipping):
        return (
            HalleZwei.objects.filter(shipping=shipping)
            .select_related("delivery_unit", "delivery_unit__material")
            .order_by("pk")
        )

    def _ready_recyclings(self):
        return (
            Recycling.objects.filter(
                status=StatusChoices.WARTET_AUF_ABHOLUNG,
                shipping__isnull=True,
            )
            .select_related("material")
            .order_by("pk")
        )

    def _ready_unloads(self):
        return (
            Unload.objects.filter(
                status=StatusChoices.WARTET_AUF_ABHOLUNG,
                shipping__isnull=True,
            )
            .select_related("material")
            .order_by("pk")
        )

    def _ready_halle_zwei(self):
        return (
            HalleZwei.objects.filter(
                status=StatusChoices.WARTET_AUF_ABHOLUNG,
                shipping__isnull=True,
            )
            .select_related("delivery_unit", "delivery_unit__material")
            .order_by("pk")
        )

    def _selected_ids(self, shipping, request=None):
        rec_ids = set(self._attached_recyclings(shipping).values_list("id", flat=True))
        unl_ids = set(self._attached_unloads(shipping).values_list("id", flat=True))
        hz_ids = set(self._attached_halle_zwei(shipping).values_list("id", flat=True))

        if request is None:
            return rec_ids, unl_ids, hz_ids

        rec_ids.update(
            int(value)
            for value in request.POST.getlist("selected_recycling")
            if value.isdigit()
        )
        unl_ids.update(
            int(value)
            for value in request.POST.getlist("selected_unload")
            if value.isdigit()
        )
        hz_ids.update(
            int(value)
            for value in request.POST.getlist("selected_halle_zwei")
            if value.isdigit()
        )
        return rec_ids, unl_ids, hz_ids

    def _has_selected_entries(self, rec_ids, unl_ids, hz_ids):
        return bool(rec_ids or unl_ids or hz_ids)

    def _context(
        self,
        *,
        shipping,
        form,
        scan_form=None,
        pre_rec=None,
        pre_unl=None,
        pre_hz=None,
    ):
        attached_recyclings = list(self._attached_recyclings(shipping))
        attached_unloads = list(self._attached_unloads(shipping))
        attached_hz = list(self._attached_halle_zwei(shipping))

        ready_recyclings = list(self._ready_recyclings())
        ready_unloads = list(self._ready_unloads())
        ready_hz = list(self._ready_halle_zwei())

        return {
            "selected_menu": "shipping_update",
            "shipping": shipping,
            "form": form,
            "scan_form": scan_form or BarcodeScanForm(),
            "recyclings": attached_recyclings + ready_recyclings,
            "unloads": attached_unloads + ready_unloads,
            "halle_zwei_units": attached_hz + ready_hz,
            "preselected_recycling_ids": pre_rec or set(),
            "preselected_unload_ids": pre_unl or set(),
            "preselected_halle_zwei_ids": pre_hz or set(),
        }

    def _set_default_value(self, form_data, field_name, value):
        if value in (None, ""):
            return

        current_value = form_data.get(field_name, "")
        if isinstance(current_value, str):
            current_value = current_value.strip()

        if current_value:
            return

        form_data[field_name] = str(value)

    def _build_prefilled_form(self, shipping, post_data):
        form_data = post_data.copy()
        barcode_data = BarcodeScanService.get_shipping_prefill_data(
            form_data.get("scan_barcode")
        )

        for form_field, barcode_field in self.GENERATED_FIELD_MAP.items():
            self._set_default_value(
                form_data, form_field, barcode_data.get(barcode_field)
            )

        form_data["scan_barcode"] = ""
        return ShippingHeaderForm(form_data, instance=shipping), BarcodeScanForm()

    def _add_scanned_target(self, target, rec_ids, unl_ids, hz_ids):
        if target["type"] == "recycling":
            rec_ids.add(target["id"])
        elif target["type"] == "unload":
            unl_ids.add(target["id"])
        elif target["type"] == "halle_zwei":
            hz_ids.add(target["id"])

    def _attach_to_shipping(self, shipping, rec_ids, unl_ids, hz_ids):
        inactive_at = timezone.now()

        if rec_ids:
            Recycling.objects.filter(pk__in=rec_ids).exclude(
                shipping=shipping,
                status=StatusChoices.ERLEDIGT,
                inactive_at__isnull=False,
            ).update(
                shipping=shipping,
                status=StatusChoices.ERLEDIGT,
                inactive_at=inactive_at,
            )
        if unl_ids:
            Unload.objects.filter(pk__in=unl_ids).exclude(
                shipping=shipping,
                status=StatusChoices.ERLEDIGT,
                inactive_at__isnull=False,
            ).update(
                shipping=shipping,
                status=StatusChoices.ERLEDIGT,
                inactive_at=inactive_at,
            )
        if hz_ids:
            HalleZwei.objects.filter(pk__in=hz_ids).exclude(
                shipping=shipping,
                status=StatusChoices.ERLEDIGT,
                inactive_at__isnull=False,
            ).update(
                shipping=shipping,
                status=StatusChoices.ERLEDIGT,
                inactive_at=inactive_at,
            )

    def get(self, request, pk):
        shipping = get_object_or_404(Shipping, pk=pk)
        form = ShippingHeaderForm(instance=shipping)
        pre_rec, pre_unl, pre_hz = self._selected_ids(shipping)

        return render(
            request,
            self.template_name,
            self._context(
                shipping=shipping,
                form=form,
                pre_rec=pre_rec,
                pre_unl=pre_unl,
                pre_hz=pre_hz,
            ),
        )

    def post(self, request, pk):
        shipping = get_object_or_404(Shipping, pk=pk)
        rec_ids, unl_ids, hz_ids = self._selected_ids(shipping, request)
        action = request.POST.get("action")

        if action == "scan_barcode":
            scan_form = BarcodeScanForm(request.POST)

            try:
                target = BarcodeScanService.get_shipping_target(
                    request.POST.get("scan_barcode"),
                    shipping=shipping,
                )
            except (BarcodeScanError, BarcodeNotFoundError) as exc:
                form = ShippingHeaderForm(request.POST, instance=shipping)
                scan_form.add_error("scan_barcode", str(exc))
                return render(
                    request,
                    self.template_name,
                    self._context(
                        shipping=shipping,
                        form=form,
                        scan_form=scan_form,
                        pre_rec=rec_ids,
                        pre_unl=unl_ids,
                        pre_hz=hz_ids,
                    ),
                )

            if target["type"] == "generated":
                form, scan_form = self._build_prefilled_form(shipping, request.POST)
                return render(
                    request,
                    self.template_name,
                    self._context(
                        shipping=shipping,
                        form=form,
                        scan_form=scan_form,
                        pre_rec=rec_ids,
                        pre_unl=unl_ids,
                        pre_hz=hz_ids,
                    ),
                )

            self._add_scanned_target(target, rec_ids, unl_ids, hz_ids)
            form = ShippingHeaderForm(request.POST, instance=shipping)
            if not form.is_valid():
                return render(
                    request,
                    self.template_name,
                    self._context(
                        shipping=shipping,
                        form=form,
                        pre_rec=rec_ids,
                        pre_unl=unl_ids,
                        pre_hz=hz_ids,
                    ),
                )

            with transaction.atomic():
                form.save()
                self._attach_to_shipping(shipping, rec_ids, unl_ids, hz_ids)

            return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))

        form = ShippingHeaderForm(request.POST, instance=shipping)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                self._context(
                    shipping=shipping,
                    form=form,
                    pre_rec=rec_ids,
                    pre_unl=unl_ids,
                    pre_hz=hz_ids,
                ),
            )

        if not self._has_selected_entries(rec_ids, unl_ids, hz_ids):
            form.add_error(
                None,
                "Bitte mindestens einen Eintrag aus 'Abholbereit / Zugeordnet' auswaehlen.",
            )
            return render(
                request,
                self.template_name,
                self._context(
                    shipping=shipping,
                    form=form,
                    pre_rec=rec_ids,
                    pre_unl=unl_ids,
                    pre_hz=hz_ids,
                ),
            )

        with transaction.atomic():
            form.save()
            self._attach_to_shipping(shipping, rec_ids, unl_ids, hz_ids)

        return redirect(reverse("shipping_update", kwargs={"pk": shipping.pk}))
