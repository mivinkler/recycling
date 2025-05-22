from django.views.generic import DetailView
from warenwirtschaft.models import Recycling, Unload

class RecyclingDetailView(DetailView):
    model = Unload
    template_name = "recycling/recycling_detail.html"
    context_object_name = "unload"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recycling_units'] = Recycling.objects.filter(unload=self.object)
        return context

