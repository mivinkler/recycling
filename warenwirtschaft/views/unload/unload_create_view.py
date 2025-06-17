from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from warenwirtschaft.forms import UnloadFormSet, DeliveryUnitForm
from warenwirtschaft.models import ReusableBarcode

class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    def get(self, request):
        return self.render_form(request)

    def post(self, request):
        form = DeliveryUnitForm(request.POST)
        formset = UnloadFormSet(request.POST, prefix='unload')

        if form.is_valid() and formset.is_valid():
            # Lieferungseinheit aus Hauptformular
            delivery_unit = form.cleaned_data['delivery_unit']
            for subform in formset:
                if not subform.cleaned_data:
                    continue
                unload = subform.save(commit=False)
                unload.delivery_unit = delivery_unit
                unload.save()
            return redirect(self.success_url)

        # Bei Fehlern Formular erneut anzeigen
        return self.render_form(request, form=form, formset=formset)

    def render_form(self, request, form=None, formset=None):
        """
        Rendert das Formular mit optionalen Fehlerdaten.
        """
        if form is None:
            form = DeliveryUnitForm()
        if formset is None:
            formset = UnloadFormSet(prefix='unload')

        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
            'empty_form': formset.empty_form,
        })
