from django.views.generic.detail import DetailView
from warenwirtschaft.models import ReusableBarcode


class ReusableBarcodeDetailView(DetailView):
    model = ReusableBarcode
    template_name = "barcode/reusable_barcode_detail.html"
    context_object_name = "barcode"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context