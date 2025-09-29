# warenwirtschaft/views/unload_create_view.py
from __future__ import annotations
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.forms.unload_form import ExistingEditFormSet, UnloadFormSet
from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService

class UnloadCreateView(View):
    template_name = "unload/unload_create.html"
    BARCODE_PREFIX = "S"

    def get(self, request, delivery_unit_pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")
        vorhandene_unloads = Unload.objects.filter(status=1).order_by("pk")
        existing_formset = ExistingEditFormSet(queryset=vorhandene_unloads, prefix="exist")
        return self.render_page(delivery_unit, formset, vorhandene_unloads, existing_formset)

    def post(self, request, delivery_unit_pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")
        vorhandene_unloads_qs = Unload.objects.filter(status=1).order_by("pk")
        existing_formset = ExistingEditFormSet(request.POST, queryset=vorhandene_unloads_qs, prefix="exist")

        selected_ids = request.POST.getlist("selected_unload")

        has_new_rows = formset.total_form_count() > 0 
        if has_new_rows and not formset.is_valid():
            return self.render_page(delivery_unit, formset, vorhandene_unloads_qs, existing_formset)
        if not existing_formset.is_valid():
            return self.render_page(delivery_unit, formset, vorhandene_unloads_qs, existing_formset)

        with transaction.atomic():
            if selected_ids:
                selected_pks: list[int] = []
                for pk in selected_ids:
                    try:
                        selected_pks.append(int(pk))
                    except (TypeError, ValueError):
                        pass
                for unload in Unload.objects.filter(status=1, pk__in=selected_pks):
                    unload.delivery_units.add(delivery_unit)

            existing_formset.save()

            if has_new_rows:
                new_instances = formset.save(commit=False)
                for instance in new_instances:
                    if not instance.status:
                        instance.status = 1
                    val = (getattr(instance, "barcode", "") or "").strip()
                    if not val:
                         instance.barcode = BarcodeNumberService.make_code(prefix=self.BARCODE_PREFIX)
                    instance.save()
                    instance.delivery_units.add(delivery_unit)

        return redirect(reverse("unload_update", kwargs={"delivery_unit_pk": delivery_unit.pk}))

    def render_page(self, delivery_unit, formset, vorhandene_unloads, existing_formset):
        return render(self.request, self.template_name, {
            "delivery_unit": delivery_unit,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_unloads": vorhandene_unloads,
            "existing_formset": existing_formset,
            "selected_menu": "unload_create",
        })
