from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from warenwirtschaft.models import DeliveryUnit

class DeliveryUnitsListView(ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_units_list.html"
    context_object_name = "delivery_units"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtering
        filter_mapping = {
            "id": "id",
            "delivery": "delivery__id",
            "delivery_date": "delivery__delivery_date",
            "delivery_id": "delivery_receipt__icontains",
            "delivery_type": "delivery_type",
            "device": "device__name__icontains",
            "weight": "weight",
            "status": "status",
            "note": "note__icontains",
        }
        filters = {
            field: self.request.GET.get(param)
            for param, field in filter_mapping.items()
            if self.request.GET.get(param)
        }
        if filters:
            queryset = queryset.filter(Q(**filters))

        # Sorting
        sort_mapping = {
            "id_asc": "id",
            "id_desc": "-id",
            "delivery_asc": "delivery__id",
            "delivery_desc": "-delivery__id",
            "date_asc": "delivery__delivery_date",
            "date_desc": "-delivery__delivery_date",
            "lid_asc": "delivery_receipt",
            "lid_desc": "-delivery_receipt",
            "container_asc": "delivery_type",
            "container_desc": "-delivery_type",
            "device_asc": "device__name",
            "device_desc": "-device__name",
            "weight_asc": "weight",
            "weight_desc": "-weight",
            "status_asc": "status",
            "status_desc": "-status",
            "note_asc": "note",
            "note_desc": "-note",
        }
        sort_field = sort_mapping.get(self.request.GET.get("sort", "id_asc"), "id")
        queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delivery_types"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES

        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        return context
