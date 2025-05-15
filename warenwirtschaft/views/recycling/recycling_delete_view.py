from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models.recycling import Recycling

class RecyclingDeleteView(DeleteView):
    model = Recycling
    template_name = 'recycling/recycling_delete.html'
    context_object_name = 'recycling'
    success_url = reverse_lazy('recycling_list')