from django.views.generic import ListView
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

from warenwirtschaft.models.shipping_unit import ShippingUnit


class ShippingUnitsListView(ListView):
    model = ShippingUnit
    template_name = "shipping/shipping_units_list.html"
    context_object_name = "shipping_units"
    paginate_by = 50

    sortable_fields = [
        ("shipping__id", "LID"),
        ("shipping__customer__name", "Abholer"),
        ("shipping__delivery_receipt", "Begleitschein"),
        ("note", "Anmerkung"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("created_at", "Datum"),
        ("status", "Status"),
    ]

    def get_queryset(self):
        sort_fields = [field[0] for field in self.sortable_fields]
        queryset = ShippingUnit.objects.select_related("units_for_shipping", "units_for_shipping__customer", "material_for_shipping_units")

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
            "box_types": ShippingUnit.BOX_TYPE_CHOICES,
            "statuses": ShippingUnit.STATUS_CHOICES,
            "selected_menu": "shipping_units_list",
        })

        return context
