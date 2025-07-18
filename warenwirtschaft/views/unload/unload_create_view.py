import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.forms import DeliveryUnitForm, UnloadFormSet
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request, *args, **kwargs):
        form = DeliveryUnitForm()
        formset = UnloadFormSet(prefix='unload')
        empty_form = formset.empty_form

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': empty_form,
            'selected_menu': 'unload_create',
        })

    def post(self, request, *args, **kwargs):
        form = DeliveryUnitForm(request.POST)
        formset = UnloadFormSet(request.POST, prefix='unload')
        empty_form = formset.empty_form

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Holt Liefereinheit aus dem Formular
                delivery_unit = form.cleaned_data['delivery_unit']

                for subform in formset:
                    unload = subform.save(commit=False)
                    unload.delivery_unit = delivery_unit

                    # Generiert Code und Barcode
                    suffix = uuid.uuid4().hex[:8].upper()
                    code = f"U{suffix}"
                    unload.code = code
                    BarcodeGenerator(unload, code, 'barcodes/unload').generate_image()
                    unload.save()

            return redirect(self.success_url)

        # Bei Fehlern Formulare erneut anzeigen
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': empty_form,
            'selected_menu': 'unload_create',
        })
