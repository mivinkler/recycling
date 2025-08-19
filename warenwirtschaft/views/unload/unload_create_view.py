import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.forms_neu.unload_form import DeliveryUnitChoiceForm, get_unload_formset
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request, *args, **kwargs):
        form = DeliveryUnitChoiceForm()
        formset_class = get_unload_formset(extra=1)
        formset = formset_class(prefix='unload')

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
            'selected_menu': 'unload_create',
        })

    def post(self, request, *args, **kwargs):
        form = DeliveryUnitChoiceForm(request.POST)
        formset_class = get_unload_formset(extra=1)
        formset = formset_class(request.POST, prefix='unload')

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                delivery_unit = form.cleaned_data['delivery_unit']

                for subform in formset:
                    unload = subform.save(commit=False)
                    unload.delivery_unit = delivery_unit

                    suffix = uuid.uuid4().hex[:8].upper()
                    code = f"U{suffix}"
                    unload.code = code
                    BarcodeGenerator(unload, code, 'barcodes/unload').generate_image()
                    unload.save()

            return redirect(self.success_url)

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
            'selected_menu': 'unload_create',
        })
