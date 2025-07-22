from django.views.generic import ListView
from warenwirtschaft.models.material import Material

class MaterialListView(ListView):
    model = Material
    template_name = "material/material_list.html"
    context_object_name = "material_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['selected_menu'] = 'material_list'
        return context