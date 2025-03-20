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
        "id", 
        "supplier__name", 
        "units", 
        "delivery_receipt", 
        "total_weight", 
        "created_at", 
        "note", 
        "delivery_units__id", 
        "delivery_units__delivery_receipt",
        "delivery_units__delivery_type", 
        "delivery_units__material__name",
        "delivery_units__weight", 
        "delivery_units__status", 
        "delivery_units__note",
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            first_unit_weight=Subquery(
                DeliveryUnit.objects.filter(delivery=OuterRef("id"))
                .order_by("id")
                .values("weight")[:1]
            )
        ).prefetch_related("deliveryunits")

        search_service = SearchService(self.request, self.active_fields)
        sorting_service = SortingService(self.request, self.active_fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")

        return context