from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models import ReusableBarcode

class ReusableBarcodeDeleteView(DeleteView):
    model = ReusableBarcode
    template_name = "barcode/reusable_barcode_delete.html"
    context_object_name = 'barcode'
    success_url = reverse_lazy('reusable_barcode_list')