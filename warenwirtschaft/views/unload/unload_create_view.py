from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from warenwirtschaft.forms import UnloadFormSet, DeliveryUnitForm
from warenwirtschaft.models import ReusableBarcode
from warenwirtschaft.services.barcode_service import generate_barcode
from warenwirtschaft.models import Unload

class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        unit_id = request.GET.get("unit_id")

        initial_data = {}
        delivery_unit_id = None

        if code:
            try:
                reusable = ReusableBarcode.objects.get(code=code, step=1)
                initial_data = {
                    'box_type': reusable.box_type,
                    'material': reusable.material_id,
                    'target': reusable.target,
                }
            except ReusableBarcode.DoesNotExist:
                pass

        elif unit_id:  # unit_id ist ID Unload
            try:
                existing_unload = Unload.objects.get(id=unit_id)
                initial_data = {
                    'box_type': existing_unload.box_type,
                    'material': existing_unload.material_id,
                    'target': existing_unload.target,
                    'weight': existing_unload.weight,
                    'note': existing_unload.note,
                }
                delivery_unit_id = existing_unload.delivery_unit_id
            except Unload.DoesNotExist:
                pass

        form = DeliveryUnitForm(initial={'delivery_unit': delivery_unit_id} if delivery_unit_id else None)
        formset = UnloadFormSet(prefix='unload', initial=[initial_data] if initial_data else [{}])

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
        })


    def post(self, request):
        form = DeliveryUnitForm(request.POST)
        formset = UnloadFormSet(request.POST, prefix='unload')

        if form.is_valid() and formset.is_valid():
            delivery_unit = form.cleaned_data['delivery_unit']
            for subform in formset:
                if not subform.cleaned_data:
                    continue
                unload = subform.save(commit=False)
                unload.delivery_unit = delivery_unit

                generate_barcode(unload)

                unload.save()
            return redirect(self.success_url)

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
        })
