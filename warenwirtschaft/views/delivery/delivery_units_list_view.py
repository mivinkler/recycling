from django.views.generic import ListView
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class DeliveryUnitsListView(ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_units_list.html"
    context_object_name = "delivery_units"
    paginate_by = 50

    sortable_fields = [
        ("delivery__id", "LID"),
        ("delivery__supplier__name", "Lieferant"),
        ("delivery__delivery_receipt", "Lieferschein"),
        ("note", "Anmerkung"),
        ("delivery_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("created_at", "Datum"),
        ("status", "Status"),
    ]

    def get_queryset(self):
        sort_fields = [field[0] for field in self.sortable_fields]
        queryset = DeliveryUnit.objects.select_related("delivery", "delivery__supplier", "material")

        queryset = SearchService(self.request, sort_fields).apply_search(queryset)
        queryset = SortingService(self.request, sort_fields).apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context.update({
            "page_obj": page_obj,
            "sort_param": self.request.GET.get("sort", ""),
            "search_query": self.request.GET.get("search", ""),
            "delivery_types": DeliveryUnit.DELIVERY_TYPE_CHOICES,
            "statuses": DeliveryUnit.STATUS_CHOICES,
            "selected_menu": "delivery_units_list",
        })

        return context
