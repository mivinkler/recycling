from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from warenwirtschaft.models import Delivery, DeliveryUnit
from django.db.models import OuterRef, Subquery
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class DeliveryListView(ListView):
    model = Delivery
    template_name = "delivery/delivery_list.html"
    context_object_name = "deliveries"
    paginate_by = 20

    active_fields = [
        ("id", "LID"),
        ("supplier__name", "Lieferant"),
        ("delivery_receipt", "Lieferschein"),
        ("created_at", "Datum"),
        ("note", "Anmerkung"),
        ("deliveryunits__delivery_type", "Behälter"),
        ("deliveryunits__material__name", "Material"),
        ("deliveryunits__weight", "Gewicht"),
        ("deliveryunits__status", "Status"),
    ]
    
    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("deliveryunits")

        fields = [field[0] for field in self.active_fields]  # Wir nehmen nur die Schlüssel

        queryset = SearchService(self.request, fields).apply_search(queryset)
        queryset = SortingService(self.request, fields).apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["search_query"] = self.request.GET.get("search", "")
        context["active_fields"] = self.active_fields
        context["selected_menu"] = "delivery_list"

        return context