from django.views.generic import ListView
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

# TODO Pagination

class RecyclingListView(ListView):
    model = Recycling
    template_name = "recycling/recycling_list.html"
    context_object_name = "recycling"
    paginate_by = 22

    active_fields = [
        "id",
        "unload",
        "box_type",
        "weight",
        "target",
        "material",
        "note",
    ]

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            queryset = super().get_queryset().select_related("recycling_for_unload", "material_for_recycling")
            search_service = SearchService(self.request, self.active_fields)
            sorting_service = SortingService(self.request, self.active_fields)

            queryset = search_service.apply_search(queryset)
            queryset = sorting_service.apply_sorting(queryset)

            self._queryset = queryset
        return self._queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["box_type"] = Recycling.BOX_TYPE_CHOICES
        context["status"] = Recycling.STATUS_CHOICES
        context["selected_menu"] = "recycling_list"

        return context
