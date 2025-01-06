from django.views.generic import DetailView
from django.core.paginator import Paginator
from warenwirtschaft.models import Delivery

class DeliveryDetailView(DetailView):
    model = Delivery
    template_name = 'delivery/delivery_detail.html'
    context_object_name = 'delivery'
    
    def get_queryset(self):
        # Используем правильное имя для prefetch_related
        queryset = super().get_queryset().prefetch_related('deliveryunits_set')  

        sort_mapping = {
            "id_asc": "id", "id_desc": "-id",
            "delivery_type_asc": "deliveryunits__delivery_type", "delivery_type_desc": "-deliveryunits__delivery_type",
            "device_asc": "deliveryunits__device", "device_desc": "-deliveryunits__device",
            "weight_asc": "weight", "weight_desc": "-weight",
            "status_asc": "deliveryunits__status", "status_desc": "-deliveryunits__status",
            "note_asc": "note", "note_desc": "-note",
        }
        sort_field = sort_mapping.get(self.request.GET.get("sort", "id_asc"), "id")
        queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request'] = self.request  # Передаем запрос в контекст
        
        delivery = self.object

        # Убедитесь, что имя связи верное
        delivery_units = delivery.deliveryunits_set.all()  

        paginator = Paginator(delivery_units, 14)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context
