from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models import Unload

class RecyclingDeleteView(DeleteView):
    model = Unload
    template_name = 'recycling/recycling_delete.html'
    context_object_name = 'unload'
    success_url = reverse_lazy('recycling_list')