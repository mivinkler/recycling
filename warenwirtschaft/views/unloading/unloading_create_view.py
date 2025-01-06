from django.views.generic import ListView
from django.core.paginator import Paginator
from warenwirtschaft.models import DeliveryUnits

class UnloadingCreateView(ListView):
    model = DeliveryUnits
    template_name = "unloading/unloading_create.html"
    context_object_name = "unloading_units"

    def get_queryset(self):
        # gibt die Objekte mit Status 1 zurück
        return DeliveryUnits.objects.filter(status=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delivery_types"] = DeliveryUnits.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnits.STATUS_CHOICES

        paginator = Paginator(self.get_queryset(), 6)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        return context