from django.views.generic import DetailView
from warenwirtschaft.models import Unload

class UnloadBarcodeView(DetailView):
    model = Unload
    template_name = 'unload/unload_barcode.html'
    context_object_name = 'unload'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["box_type"] = Unload.box_type
        context["statuses"] = Unload.status

        return context
