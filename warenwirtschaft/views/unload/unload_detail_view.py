from django.views.generic import DetailView
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.unload import Unload  # импорт модели Unload

class UnloadDetailView(DetailView):
    model = DeliveryUnit
    template_name = 'unload/unload_detail.html'
    context_object_name = 'delivery_unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # expliziter ORM-Zugriff auf die Unload-Einträge dieser Liefereinheit
        context['unloads'] = Unload.objects.filter(delivery_unit=self.object)
        return context
