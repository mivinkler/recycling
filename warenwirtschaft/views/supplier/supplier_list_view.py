from django.views.generic import ListView
from django.db.models import Q
from warenwirtschaft.models import Supplier
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class SupplierListView(ListView):
    model = Supplier
    template_name = "supplier/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 20

    active_fields= [
        "id", 
        "avv_number", 
        "name", 
        "street", 
        "postal_code", 
        "city", 
        "phone", 
        "email", 
        "note"
        ]
    
    def get_queryset(self):
        queryset = super().get_queryset()

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
        return context
