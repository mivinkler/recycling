from django.views.generic.detail import DetailView
from warenwirtschaft.models import Supplier, Delivery
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = "supplier/supplier_detail.html"
    context_object_name = "supplier"
    paginate_by = 14

    active_fields = [
        "delivery__id",
        "delivery__delivery_receipt",
        "delivery__total_weight",
        "delivery__note",
        "delivery__created_at"
    ]

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("deliveries")
        sorting_service = SortingService(self.request, self.active_fields)
        return sorting_service.apply_sorting(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        deliveries = self.object.deliveries.all()

        sorting_service = SortingService(self.request, self.active_fields)
        deliveries = sorting_service.apply_sorting(deliveries)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(deliveries)

        context["deliveries"] = page_obj
        context["page_obj"] = page_obj
        context["search_query"] = self.request.GET.get("search", "")
        context["sort"] = self.request.GET.get("sort", "id_asc")

        return context
