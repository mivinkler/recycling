from django.views.generic import DetailView
from warenwirtschaft.models.unload import Unload

class UnloadDetailView(DetailView):
    model = Unload
    template_name = "unload/unload_detail.html"
    context_object_name = "unload"
