from django.views.generic import ListView
from warenwirtschaft.models.material import Material
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class MaterialListView(ListView):
    model = Material
    template_name = "material/material_list.html"
    context_object_name = "material"
    paginate_by = 22

    active_fields = [
        ("id", "ID"),
        ("name", "Name")
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]

        search_service = SearchService(self.request, fields)
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

        return context

