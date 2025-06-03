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

    active_fields = [
        ("shipping__id", "LID"),
        ("shipping__customer__name", "Abholer"),
        ("shipping__certificate", "Begleitschein"),
        ("note", "Anmerkung"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("created_at", "Datum"),
        ("status", "Status"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "box_type": ShippingUnit.BOX_TYPE_CHOICES,
            "status": ShippingUnit.STATUS_CHOICES,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", ""),
        context["box_types"] = ShippingUnit.BOX_TYPE_CHOICES,
        context["selected_menu"] = "shipping_list"

        return context
