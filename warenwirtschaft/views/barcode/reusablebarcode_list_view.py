from django.views.generic import ListView
from warenwirtschaft.models import ReusableBarcode

class ReusableBarcodeListView(ListView):
    model = ReusableBarcode
    template_name = 'barcode/reusable_barcode_list.html'
    context_object_name = 'barcodes'
