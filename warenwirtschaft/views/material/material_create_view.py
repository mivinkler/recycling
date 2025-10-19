from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from warenwirtschaft.models.material import Material
from warenwirtschaft.forms.material_form import MaterialForm

class MaterialCreateView(CreateView):
    model = Material
    form_class = MaterialForm
    template_name = "material/material_create.html"
    success_url = reverse_lazy("material_create")
    context_object_name = "form"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["material_list"] = Material.objects.all()
        context["selected_menu"] = "material_form"
        return context
