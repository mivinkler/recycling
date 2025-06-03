from django.views.generic import ListView
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class RecyclingListView(ListView):
    model = Recycling
    template_name = "recycling/recycling_list.html"
    context_object_name = "recycling"
    paginate_by = 22

    active_fields = [
        ("id", "ID"),
        ("box_type", "Behälter"),
        ("weight", "Gewicht"),
        ("target", "Zweck"),
        ("status", "Status"),
        ("material__name", "Material"),
        ("created_at", "Datum"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "box_type": Recycling.BOX_TYPE_CHOICES,
            "status": Recycling.STATUS_CHOICES,
            "target": Recycling.TARGET_CHOICES,
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
        context["box_type"] = Recycling.BOX_TYPE_CHOICES
        context["status"] = Recycling.STATUS_CHOICES
        context["selected_menu"] = "recycling_list"

        return context
