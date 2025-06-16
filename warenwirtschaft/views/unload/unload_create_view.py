from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from warenwirtschaft.forms import UnloadFormSet, DeliveryUnitForm
from warenwirtschaft.models import ReusableBarcode

class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get_barcode_data(self, code):
        try:
            reusable = ReusableBarcode.objects.get(code=code, step=1)  # Schritt: Lieferung
            return {
                'box_type': reusable.box_type,
                'material': reusable.material,
                'target': reusable.target,
                'code': reusable.code,
            }
        except ReusableBarcode.DoesNotExist:
            return {}

    def get(self, request):
        code = request.GET.get("code")

        initial_data = self.get_barcode_data(code) if code else {}

        form = DeliveryUnitForm()
        formset = UnloadFormSet(prefix='unload', initial=[initial_data] if initial_data else [{}])

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
            'code': code,
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
                unload.save()
            return redirect(self.success_url)

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
        })
