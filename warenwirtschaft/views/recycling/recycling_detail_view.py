from django.views.generic import DetailView
from warenwirtschaft.models import Recycling

class RecyclingDetailView(DetailView):
    model = Recycling
    template_name = 'recycling/recycling_detail.html'
    context_object_name = 'recycling'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["box_type"] = Recycling.BOX_TYPE_CHOICES
        context["statuses"] = Recycling.STATUS_CHOICES

        return context
