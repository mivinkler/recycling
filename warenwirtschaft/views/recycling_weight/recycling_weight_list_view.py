from django.views.generic import ListView
from django.urls import reverse_lazy
from warenwirtschaft.models import Recycling


class RecyclingWeightListView(ListView):
    model = Recycling
    template_name = 'recycling_weight/recycling_weight_list.html'
    success_url = reverse_lazy('recycling_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['recycling'] = Recycling.objects.filter(status=1)
        return context
