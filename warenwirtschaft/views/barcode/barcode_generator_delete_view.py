from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models import BarcodeGenerator

class BarcodeGeneratorDeleteView(DeleteView):
    model = BarcodeGenerator
    template_name = "barcode/barcode_generator_delete.html"
    context_object_name = 'barcode'
    success_url = reverse_lazy('barcode_generator_list')