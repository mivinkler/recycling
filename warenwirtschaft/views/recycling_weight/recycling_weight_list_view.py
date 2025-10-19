from django.views.generic import ListView
from django.urls import reverse_lazy
from warenwirtschaft.models import Recycling


class RecyclingWeightListView(ListView):
    model = Recycling
    template_name = 'recycling_weight/recycling_weight_list.html'
    success_url = reverse_lazy('recycling_list')
    context_object_name = "form"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['recycling_list'] = Recycling.objects.filter(status=1)
        context['selected_menu'] = "recycling_weight_form"
        return context
