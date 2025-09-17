from django.views.generic import ListView
from warenwirtschaft.models import BarcodeGenerator

class BarcodeGeneratorListView(ListView):
    model = BarcodeGenerator
    template_name = 'barcode/barcode_generator_list.html'
    context_object_name = 'barcodes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'barcode_generator_list'
        context["dashboard"] = True
        return context
