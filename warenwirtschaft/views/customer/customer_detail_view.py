from django.views.generic.detail import DetailView
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.shipping_unit import ShippingUnit


class CustomerDetailView(DetailView):
    model = Customer
    template_name = "customer/customer_detail.html"
    context_object_name = "customer"
    paginate_by = 14

    sortable_fields = [
        ("shipping__id", "LID"),
        ("shipping__certificate", "Begleit-/Übernahmeschein"),
        ("weight", "Gewicht"),
        ("transport", "Transport"),
        ("note", "Anmerkung"),
        ("created_at", "Datum"),
    ]

    def get_queryset(self):
        return super().get_queryset()

    def get_shippingunits_queryset(self):
        sort_fields = [field[0] for field in self.sortable_fields]
        customer = self.get_object()

        queryset = ShippingUnit.objects.select_related("units_for_shipping", "units_for_shipping__customer", "material_for_shipping_units").filter(shipping__customer=customer)

        queryset = SearchService(self.request, sort_fields).apply_search(queryset)
        queryset = SortingService(self.request, sort_fields).apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        deliveryunits = self.get_deliveryunits_queryset()
        page_obj = PaginationService(self.request, self.paginate_by).get_paginated_queryset(shippingunits)

        context.update({
            "page_obj": page_obj,
            "shippingunits": page_obj,
            "search_query": self.request.GET.get("search", ""),
            "sort_param": self.request.GET.get("sort", ""),
            "sortable_fields": self.sortable_fields,
            "selected_menu": "shipping_list",
        })
        return context
