from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from warenwirtschaft.models.halle_zwei import HalleZwei
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class HalleZweiListView(ListView):
    model = HalleZwei
    template_name = "halle_zwei/halle_zwei_list.html"
    context_object_name = "halle-zwei"
    paginate_by = 28

    
    active_fields = [
        ("id", "HID"),
        ("delivery_units__id", "Liefereinheiten"),
        ("created_at", "Datum"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "status": HalleZwei.status,
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
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["selected_menu"] = "halle_zwei_list"
        
        context["dashboard"] = True

        return context
