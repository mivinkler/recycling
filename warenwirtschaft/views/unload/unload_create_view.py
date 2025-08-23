from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction
import uuid

from warenwirtschaft.forms_neu.unload_form import DeliveryUnitChoiceForm, UnloadFormSet
from warenwirtschaft.models import Unload
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request):
        form = DeliveryUnitChoiceForm()
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")

        existing_unloads = Unload.objects.filter(status=1)

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "existing_unloads": existing_unloads,
        })

    def post(self, request):
        form = DeliveryUnitChoiceForm(request.POST)
        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")
        existing_unloads = Unload.objects.filter(status=1)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                delivery_unit = form.cleaned_data["delivery_unit"]

                # 1) Neue Unloads aus dem Formset speichern
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

                # 2) Vorhandene Unloads verknüpfen (per Checkbox ausgewählt)
                selected_ids = request.POST.getlist("selected_unloads")
                if selected_ids:
                    Unload.objects.filter(pk__in=selected_ids).update(delivery_unit=delivery_unit)

            return redirect(self.success_url)

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "existing_unloads": existing_unloads,
        })
