from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from warenwirtschaft.models import Recycling
from warenwirtschaft.forms import RecyclingForm

class RecyclingUpdateView(UpdateView):
    model = Recycling
    form_class = RecyclingForm
    template_name = "recycling/recycling_update.html"
    context_object_name = "recycling"
    success_url = reverse_lazy("recycling_list")