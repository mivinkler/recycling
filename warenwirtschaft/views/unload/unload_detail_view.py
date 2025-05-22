from django.views.generic import DetailView
from warenwirtschaft.models import DeliveryUnit, Unload

class UnloadDetailView(DetailView):
    model = DeliveryUnit
    template_name = 'unload/unload_detail.html'
    context_object_name = 'delivery_unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unloads'] = Unload.objects.filter(delivery_unit=self.object)
        return context
