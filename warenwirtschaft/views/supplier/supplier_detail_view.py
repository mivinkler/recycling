from django.views.generic.detail import DetailView
from warenwirtschaft.models.supplier import Supplier
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = "supplier/supplier_detail.html"
    context_object_name = "supplier"
    paginate_by = 14

    sortable_fields = [
        ("delivery__id", "LID"),
        ("delivery__delivery_receipt", "Lieferschein"),
        ("weight", "Gewicht"),
        ("note", "Anmerkung"),
        ("created_at", "Datum"),
    ]

    def get_queryset(self):
        return super().get_queryset()

    def get_deliveryunits_queryset(self):
        sort_fields = [field[0] for field in self.sortable_fields]
        supplier = self.get_object()

        queryset = DeliveryUnit.objects.select_related("units_for_delivery", "units_for_delivery__supplier", "material_for_delivery_units").filter(delivery__supplier=supplier)

        queryset = SearchService(self.request, sort_fields).apply_search(queryset)
        queryset = SortingService(self.request, sort_fields).apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        deliveryunits = self.get_deliveryunits_queryset()
        page_obj = PaginationService(self.request, self.paginate_by).get_paginated_queryset(deliveryunits)

        context.update({
            "page_obj": page_obj,
            "deliveryunits": page_obj,
            "search_query": self.request.GET.get("search", ""),
            "sort_param": self.request.GET.get("sort", ""),
            "sortable_fields": self.sortable_fields,
            "selected_menu": "supplier_list",
        })
        return context
