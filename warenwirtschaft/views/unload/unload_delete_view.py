from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models.unload import Unload

class UnloadDeleteView(DeleteView):
    model = Unload
    template_name = 'unload/unload_delete.html'
    context_object_name = 'unload'
    success_url = reverse_lazy('unload_list')