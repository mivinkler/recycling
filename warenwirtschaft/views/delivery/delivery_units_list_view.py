from django.views.generic import ListView
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class DeliveryUnitsListView(ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_units_list.html"
    context_object_name = "delivery_units"
    paginate_by = 50

    active_fields = [
        ("delivery__id", "LID", "table-id"),
        ("delivery__supplier__name", "Lieferant", "table-name"),
        ("delivery__delivery_receipt", "Lieferschein", "table-delivery-receipt"),
        ("note", "Anmerkung", "table-note"),
        ("delivery_type", "Behälter", "table-delivery-type"),
        ("material__name", "Material", "table-material"),
        ("weight", "Gewicht", "table-weight"),
        ("created_at", "Datum", "table-data"),
        ("status", "Status", "table-status"),
    ]

    def get_queryset(self):
        fields = [field[0] for field in self.active_fields]  # Wir nehmen nur die Schlüssel
        queryset = DeliveryUnit.objects.select_related("delivery", "delivery__supplier", "material")
        
        queryset = SearchService(self.request, fields).apply_search(queryset)
        queryset = SortingService(self.request, fields).apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["selected_menu"] = "delivery_units_list"

        context["delivery_types"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES

        return context
