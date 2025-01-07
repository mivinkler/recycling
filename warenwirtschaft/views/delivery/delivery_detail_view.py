from django.views.generic import DetailView
from django.core.paginator import Paginator
from warenwirtschaft.models import Delivery


class DeliveryDetailView(DetailView):
    model = Delivery
    template_name = 'delivery/delivery_detail.html'
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        delivery = self.object

        sort_mapping = {
            "id_asc": "id", "id_desc": "-id",
            "delivery_type_asc": "delivery_type", "delivery_type_desc": "-delivery_type",
            "device_asc": "device", "device_desc": "-device",
            "weight_asc": "weight", "weight_desc": "-weight",
            "status_asc": "status", "status_desc": "-status",
            "note_asc": "note", "note_desc": "-note",
        }
        sort_param = self.request.GET.get("sort", "id_asc")
        sort_field = sort_mapping.get(sort_param, "id")

        # Sortieren Liefereinheiten
        delivery_units = delivery.deliveryunits.all().order_by(sort_field)

        paginator = Paginator(delivery_units, 14)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['sort_param'] = sort_param  # Übergeben der aktuellen Sortierung an html
        return context
