from django.views.generic import ListView
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class UnloadListView(ListView):
    model = Unload
    template_name = "unload/unload_list.html"
    context_object_name = "unloads"
    paginate_by = 22

    active_fields = [
        ("id", "ID"),
        ("delivery_unit__delivery__id", "LD"),
        ("delivery_unit__id", "LED"),
        ("delivery_unit__delivery__supplier__name", "Lieferant"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("target", "Ziel"),
        ("status", "Status"),
        ("created_at", "Datum"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]
        
        choices_fields={
            "box_type": Unload.BOX_TYPE_CHOICES,
            "status": Unload.STATUS_CHOICES,
            "target": Unload.TARGET_CHOICES,
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
        context["box_type"] = Unload.BOX_TYPE_CHOICES
        context["status"] = Unload.STATUS_CHOICES
        context["selected_menu"] = "unload_list"

        return context
