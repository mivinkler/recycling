from django.views.generic import DetailView
from warenwirtschaft.models import Recycling

class RecyclingDetailView(DetailView):
    model = Recycling
    template_name = "recycling/recycling_detail.html"
    context_object_name = "recycling"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unloads'] = self.object.unloads.all()
        context['recycling_units'] = [self.object]
        return context

