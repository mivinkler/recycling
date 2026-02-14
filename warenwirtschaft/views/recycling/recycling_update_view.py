from django.urls import reverse
from django.views.generic import UpdateView

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models import Recycling


class RecyclingUpdateView(UpdateView):
    """
    Bearbeitet eine einzelne Recycling-Fraktion (Eintrag).
    Nach dem Speichern bleibt der Benutzer auf derselben Seite.
    """
    model = Recycling
    form_class = RecyclingForm
    template_name = "recycling/recycling_update.html"
    context_object_name = "recycling"

    def get_success_url(self):
        # Bleibt auf derselben Update-Seite
        return reverse("recycling_update", kwargs={"pk": self.object.pk})

