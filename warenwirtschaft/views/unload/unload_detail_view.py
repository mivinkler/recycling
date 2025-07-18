from django.views.generic import DetailView
from warenwirtschaft.models import DeliveryUnit, Unload

class UnloadDetailView(DetailView):
    model = Unload
    template_name = 'unload/unload_detail.html'
    context_object_name = 'unload'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["box_type"] = Unload.BOX_TYPE_CHOICES
        context["statuses"] = Unload.STATUS_CHOICES

        return context
