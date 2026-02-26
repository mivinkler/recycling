from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class HalleZweiListView(ListView):
    model = Unload
    template_name = "device_check/device_check_list.html"
    context_object_name = "device-checks"
    paginate_by = 28

    
    active_fields = [
        ("id", "HID"),
        ("unloads__id", "Vorsortierung"),
        ("recyclins__id", "Zerlegung"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("purpose", "Zweck"),
        ("created_at", "Datum"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "box_type": Unload.box_type,
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
        context["box_type"] = Unload.box_type
        context["purpose"] = Unload.purpose
        context["selected_menu"] = "device_check_list"
        
        context["dashboard"] = True

        return context
