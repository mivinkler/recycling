from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from warenwirtschaft.models import Unload
from warenwirtschaft.forms_neu.unload_form import UnloadForm


class UnloadItemUpdateView(UpdateView):
    model = Unload
    form_class = UnloadForm
    template_name = 'unload/unload_item_update.html'
    context_object_name = 'unload'
    success_url = reverse_lazy('unload_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context