from django.views.generic import ListView
from warenwirtschaft.models import ReusableBarcode

class ReusableBarcodeListView(ListView):
    model = ReusableBarcode
    template_name = 'barcode/reusable_barcode_list.html'
    context_object_name = 'barcodes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'reusable_barcode_list'
        context["dashboard"] = True
        return context
