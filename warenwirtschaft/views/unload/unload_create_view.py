# -*- coding: utf-8 -*-
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction
import uuid

from warenwirtschaft.models import Unload
from warenwirtschaft.forms_neu.unload_form import DeliveryUnitForm, UnloadFormSet, ExistingEditFormSet
from warenwirtschaft.services.barcode_service import BarcodeGenerator




class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request):
        form = DeliveryUnitForm()
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")

        existing_qs = Unload.objects.filter(status=1).order_by('pk')
        existing_formset = ExistingEditFormSet(queryset=existing_qs, prefix="exist")

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "existing_qs": existing_qs,
            "existing_formset": existing_formset,
        })

    def post(self, request):
        form = DeliveryUnitForm(request.POST)
        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")

        existing_qs = Unload.objects.filter(status=1).order_by('pk')
        existing_formset = ExistingEditFormSet(request.POST, queryset=existing_qs, prefix="exist")

        selected_pk = request.POST.get("selected_recycling")

        if form.is_valid() and formset.is_valid() and existing_formset.is_valid():
            with transaction.atomic():
                delivery_unit = form.cleaned_data["delivery_unit"]

                # DE: Neue Unloads speichern
                for subform in formset:
                    if not subform.cleaned_data:
                        continue
                    unload = subform.save(commit=False)
                    unload.delivery_unit = delivery_unit
                    suffix = uuid.uuid4().hex[:8].upper()
                    code = f"U{suffix}"
                    unload.code = code
                    unload.save()
                    BarcodeGenerator(unload, code, 'barcodes/unload').generate_image()

                # DE: Nur die per Radio ausgewählte bestehende Zeile speichern (Status + Gewicht)
                if selected_pk:
                    for f in existing_formset.forms:
                        if str(f.instance.pk) == str(selected_pk):
                            f.save()
                            break

                # (Optional) deine прежняя логика массовой привязки:
                selected_ids = request.POST.getlist("selected_unloads")
                if selected_ids:
                    Unload.objects.filter(pk__in=selected_ids).update(delivery_unit=delivery_unit)

            return redirect(self.success_url)

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "existing_qs": existing_qs,
            "existing_formset": existing_formset,
        })
