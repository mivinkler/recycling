from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from warenwirtschaft.models import Unload
from warenwirtschaft.forms import UnloadForm


class UnloadUpdateView(UpdateView):
    model = Unload
    form_class = UnloadForm
    template_name = 'unload/unload_update.html'
    context_object_name = 'unload'
    success_url = reverse_lazy('unload_list')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        print("DEBUG: geladenes Unload-Objekt:", self.object)
        print("DEBUG: initial data:", self.get_form().initial)
        return super().get(request, *args, **kwargs)