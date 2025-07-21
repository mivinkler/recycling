from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from warenwirtschaft.models import Recycling
from warenwirtschaft.forms import RecyclingForm


class RecyclingUpdateWeightView(FormView):
    form_class = RecyclingForm
    template_name = 'recycling/recycling_update_weight.html'
    success_url = reverse_lazy('recycling_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['recycling'] = Recycling.objects.filter(status=1)
        return context
