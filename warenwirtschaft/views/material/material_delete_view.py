from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models.material import Material

class MaterialDeleteView(DeleteView):
    model = Material
    template_name = "material/material_delete.html"
    success_url = reverse_lazy("material_create")
