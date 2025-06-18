from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from warenwirtschaft.forms import UnloadFormSet, DeliveryUnitForm
from warenwirtschaft.models import ReusableBarcode

class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request):
        """
        Zeigt leeres Formular für Umladungserfassung.
        Falls ein Barcode gescannt wurde, werden zugehörige Felder vorausgefüllt.
        """
        code = request.GET.get("code", "").strip().upper()

        initial_data = {}
        if code:
            try:
                reusable = ReusableBarcode.objects.get(code=code, step=1)
                initial_data = {
                    'box_type': reusable.box_type,
                    'material': reusable.material_id,
                    'target': reusable.target,
                }
            except ReusableBarcode.DoesNotExist:
                pass  # Kein Fehler anzeigen – Benutzer kann manuell ausfüllen

        form = DeliveryUnitForm()
        formset = UnloadFormSet(prefix='unload', initial=[initial_data] if initial_data else [{}])

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
        })

    def post(self, request):
        """
        Verarbeitet das Abschicken des Formulars.
        """
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
