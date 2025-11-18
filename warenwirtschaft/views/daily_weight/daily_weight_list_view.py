from django.views.generic import TemplateView
from warenwirtschaft.models import Recycling
from warenwirtschaft.models import Unload

class DailyWeightListView(TemplateView):
    template_name = 'daily_weight/daily_weight_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['recycling_list'] = Recycling.objects.filter(status=1)
        context['unload_list'] = Unload.objects.filter(status=1)
        context['selected_menu'] = "daily_weight"

        return context
