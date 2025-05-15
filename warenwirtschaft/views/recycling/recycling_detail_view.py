from django.views.generic import DetailView
from warenwirtschaft.models.recycling import Recycling

class RecyclingDetailView(DetailView):
    model = Recycling
    template_name = "recycling/recycling_detail.html"
    context_object_name = "recycling"
