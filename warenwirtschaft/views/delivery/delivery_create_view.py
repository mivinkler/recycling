# -*- coding: utf-8 -*-
from django.views.generic.edit import CreateView
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.forms.delivery_form import DeliveryForm, get_delivery_unit_formset
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService

class DeliveryCreateView(CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'delivery/delivery_create.html'
    context_object_name = 'delivery'
    success_url = reverse_lazy('delivery_list')

    BARCODE_PREFIX = "L"  # Prefix für Lieferung

    def get_context_data(self, **kwargs):
        # Kontext vorbereiten: Hauptformular + Inline-Formset
        context = super().get_context_data(**kwargs)
        DeliveryUnitFormSet = get_delivery_unit_formset(extra=1)

        if self.request.POST:
            context['formset'] = DeliveryUnitFormSet(self.request.POST)
        else:
            context['formset'] = DeliveryUnitFormSet()

        context['empty_form'] = context['formset'].empty_form
        context["selected_menu"] = "delivery_create"
        return context

    def form_valid(self, form):
        # Erst das Hauptformular validieren/speichern
        context = self.get_context_data()
        formset = context['formset']

        if not formset.is_valid():
            context['form'] = form
            return self.render_to_response(context)

        with transaction.atomic():
            # 1) Lieferung speichern (FK für Units vorhanden)
            self.object = form.save()
            formset.instance = self.object

            # 2) Units ohne Commit holen, Barcode setzen (falls leer) und speichern
            units = formset.save(commit=False)
            for unit in units:
                # leere/Whitespace-Barcodes als "leer" behandeln
                val = (getattr(unit, "barcode", "") or "").strip()
                if not val:
                    unit.barcode = BarcodeNumberService.make_code(prefix=self.BARCODE_PREFIX)
                unit.save()

        return super().form_valid(form)
