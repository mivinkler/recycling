import uuid
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.http import HttpResponseRedirect

from warenwirtschaft.models import ReusableBarcode
from warenwirtschaft.forms import ReusableBarcodeForm
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class ReusableBarcodeCreateView(CreateView):
    model = ReusableBarcode
    form_class = ReusableBarcodeForm
    template_name = 'barcode/reusable_barcode_create.html'

    AREA_PREFIX = {
        1: "L",  # Lieferung (Wareneingang)
        2: "S",  # Vorsortierung
        3: "V",  # Abholung (Versand)
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'reusable_barcode_create'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)

        prefix = self.AREA_PREFIX[self.object.area]
        suffix = uuid.uuid4().hex[:8].upper()
        
        code = f"{prefix}{suffix}"
        self.object.code = code

        BarcodeGenerator(self.object, code, 'barcodes/reusable').generate_image()
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('reusable_barcode_detail', kwargs={'pk': self.object.pk})
