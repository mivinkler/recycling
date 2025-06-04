from django.views.generic.edit import FormView
from django.shortcuts import redirect, render
from django.db import transaction
from django.urls import reverse_lazy
from warenwirtschaft.forms import UnloadFormSet, DeliveryUnitForm
from warenwirtschaft.models import DeliveryUnit, Delivery

class UnloadCreateView(FormView):
    template_name = 'unload/unload_create.html'
    form_class = DeliveryUnitForm
    success_url = reverse_lazy('unload_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form') or self.get_form()
        context['form'] = form

        if hasattr(self, 'formset'):
            context['formset'] = self.formset
        else:
            context['formset'] = UnloadFormSet(prefix='unload')

        context['empty_form'] = context['formset'].empty_form
        return context

    def post(self, request, *args, **kwargs):
        # Barcode aus POST lesen
        scanned_barcode = request.POST.get("barcode")

        # Suche DeliveryUnit anhand des Barcodes
        delivery_unit = None
        if scanned_barcode:
            try:
                delivery = Delivery.objects.get(barcode=scanned_barcode)
                delivery_unit = DeliveryUnit.objects.filter(delivery=delivery).first()  # можно уточнить фильтр
            except Delivery.DoesNotExist:
                delivery_unit = None

        if delivery_unit:
            form = DeliveryUnitForm(initial={'delivery_unit': delivery_unit})
            self.formset = UnloadFormSet(request.POST, instance=delivery_unit, prefix='unload')
        else:
            form = self.get_form()
            self.formset = UnloadFormSet(request.POST, prefix='unload')

        if self.formset.is_valid():
            with transaction.atomic():
                self.formset.save()
            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        # Wird nicht verwendet, da wir alles über post() machen
        return super().form_valid(form)
