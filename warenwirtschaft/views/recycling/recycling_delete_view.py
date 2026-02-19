from django.views.generic.edit import DeleteView
from django.shortcuts import get_object_or_404
from django.urls import reverse

from warenwirtschaft.models import Recycling, Unload


class RecyclingDeleteView(DeleteView):
    model = Recycling
    template_name = 'recycling/recycling_delete.html'
    context_object_name = 'recycling'

    def get_object(self, queryset=None):
        # Nur Recycling löschen, der mit Unload verknüpft ist
        return get_object_or_404(
            Recycling,
            pk=self.kwargs["recycling_pk"],
            unloads__pk=self.kwargs["unload_pk"],
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unload"] = get_object_or_404(
            Unload,
            pk=self.kwargs["unload_pk"],
        )
        return context
    
    def get_success_url(self):
        return reverse(
            "recycling_create",
            kwargs={"unload_pk": self.kwargs["unload_pk"]},
        )