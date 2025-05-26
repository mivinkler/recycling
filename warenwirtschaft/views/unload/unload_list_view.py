from django.views.generic import ListView
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class UnloadListView(ListView):
    model = Unload
    template_name = "unload/unload_list.html"
    context_object_name = "unloads"
    paginate_by = 22

    active_fields = [
        "id",
        "supplier__name",
        "delivery_unit",
        "box_type",
        "material",
        "weight",
        "target",
        "note",
    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("delivery_unit", "material")
           
        fields = [field[0] for field in self.active_fields]
        search_service = SearchService(self.request, fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["box_type"] = Unload.BOX_TYPE_CHOICES
        context["status"] = Unload.STATUS_CHOICES
        context["selected_menu"] = "unload_list"

        return context
