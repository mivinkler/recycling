# warenwirtschaft/views/device_check/device_check_create_view.py
# -*- coding: utf-8 -*-
from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.device_check_form import get_device_check_formset
from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.models.device_check import DeviceCheck
from warenwirtschaft.models_common.choices import StatusChoices


class DeviceCheckCreateView(View):
    template_name = "device_check/device_check_create.html"
    NEW_PREFIX = "new"
    EXTRA_ROWS = 1

    def _get_source(self, source: str, pk: int):
        # Quelle ermitteln + passendes QuerySet
        if source == "unload":
            obj = get_object_or_404(Unload, pk=pk)
            qs = DeviceCheck.objects.filter(unload=obj).order_by("pk")
            return obj, qs
        if source == "recycling":
            obj = get_object_or_404(Recycling, pk=pk)
            qs = DeviceCheck.objects.filter(recycling=obj).order_by("pk")
            return obj, qs
        raise ValueError("Ungültige Quelle")

    def get(self, request, source: str, pk: int):
        source_obj, qs = self._get_source(source, pk)
        FormSet = get_device_check_formset(extra=self.EXTRA_ROWS)
        formset = FormSet(queryset=qs, prefix=self.NEW_PREFIX)
        return render(request, self.template_name, {"source_obj": source_obj, "formset": formset})

    def post(self, request, source: str, pk: int):
        source_obj, qs = self._get_source(source, pk)
        action = request.POST.get("action")

        FormSet = get_device_check_formset(extra=0)
        formset = FormSet(data=request.POST, queryset=qs, prefix=self.NEW_PREFIX)

        # Leere Zeilen (z.B. per "+" hinzugefügt) nicht validieren
        for f in formset.forms:
            if not f.has_changed():
                f.empty_permitted = True

        if not formset.is_valid():
            return render(request, self.template_name, {"source_obj": source_obj, "formset": formset})

        with transaction.atomic():
            # Löschen
            for f in formset.deleted_forms:
                if f.instance.pk:
                    f.instance.delete()

            # Speichern
            for f in formset.forms:
                if f in formset.deleted_forms or not f.has_changed():
                    continue

                obj = f.save(commit=False)

                # Neue Einträge mit Quelle verknüpfen
                if obj.pk is None:
                    obj.material = getattr(source_obj, "material", None)
                    if source == "unload":
                        obj.unload = source_obj
                        obj.recycling = None
                    else:
                        obj.recycling = source_obj
                        obj.unload = None

                obj.save()

            # Status setzen
            source_obj.status = (
                StatusChoices.ABHOLBEREIT
                if action == "finish_device_check"
                else StatusChoices.IN_HALLE_ZWEI
            )
            source_obj.save(update_fields=["status"])

        return redirect("device_check_select") if action == "finish_device_check" else redirect(
            reverse("device_check_create", kwargs={"source": source, "pk": pk})
        )
