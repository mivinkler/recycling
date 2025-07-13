import uuid
from django.views import View
from django.shortcuts import render
from django.db import transaction
from django.urls import reverse_lazy
from django.shortcuts import redirect

from warenwirtschaft.models import Unload
from warenwirtschaft.forms import UnloadFormSet, DeliveryUnitForm
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get_context_data(self, post_data=None):
        if post_data is None:
            post_data = None

        form = DeliveryUnitForm(post_data)
        formset = UnloadFormSet(post_data, prefix='unload')
        empty_form = formset.empty_form

        return {
            'form': form,
            'formset': formset,
            'empty_form': empty_form,
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context["selected_menu"] = "unload_create"
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request.POST)
        form = context['form']
        formset = context['formset']

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

        return render(request, self.template_name, context)
