from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.edit import DeleteView

from warenwirtschaft.models import Recycling


class RecyclingDeleteView(DeleteView):
    model = Recycling
    template_name = "recycling/recycling_delete.html"
    context_object_name = "recycling"
    pk_url_kwarg = "recycling_pk"

    def get_object(self, queryset=None):
        # Recycling nur nach ID laden
        return get_object_or_404(Recycling, pk=self.kwargs["recycling_pk"])

    def get_success_url(self):
        # Nach dem Löschen zurück zur Übersicht
        return reverse("recycling_create")