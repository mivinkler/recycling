from django.views.generic.edit import CreateView
from warenwirtschaft.forms import UnloadForm
from warenwirtschaft.models import Material
from warenwirtschaft.models import Unload


class UnloadCreateView(CreateView):
    model = Unload
    template_name = "unload/unload_create.html"
    form_class = UnloadForm   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_obj"] = Unload.objects.select_related("delivery_unit").all()
        context["materials"] = Material.objects.only("id", "name")

        return context