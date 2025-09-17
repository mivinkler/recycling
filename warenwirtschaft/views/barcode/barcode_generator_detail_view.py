from django.views.generic.detail import DetailView
from django.conf import settings

from warenwirtschaft.models import BarcodeGenerator


class BarcodeGeneratorDetailView(DetailView):
    model = BarcodeGenerator
    template_name = "barcode/barcode_generator_detail.html"
    context_object_name = "barcode"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context