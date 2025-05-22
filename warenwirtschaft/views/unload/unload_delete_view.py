from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models import DeliveryUnit

class UnloadDeleteView(DeleteView):
    model = DeliveryUnit
    template_name = 'unload/unload_delete.html'
    context_object_name = 'delivery_unit'
    success_url = reverse_lazy('unload_list')