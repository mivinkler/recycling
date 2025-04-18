from django.views.generic.detail import DetailView
from warenwirtschaft.models import Supplier
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.search_service import SearchService
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
        queryset = super().get_queryset().prefetch_related("deliveries", "deliveries__deliveryunits", "deliveries__deliveryunits__material")

        search_service = SearchService(self.request, self.active_fields)
        sorting_service = SortingService(self.request, self.active_fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        deliveries = self.object.deliveries.all()
        deliveries = deliveries.order_by('id')

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(deliveries)

        context["page_obj"] = page_obj
        context["deliveries"] = page_obj
        context["deliveryunits"] = page_obj
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")

        return context
