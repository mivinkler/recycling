from django.views.generic import ListView
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models import DeliveryUnit
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
        "unload_type",
        "material",
        "weight",
        "purpose",
        "note",
    ]

    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            queryset = super().get_queryset().select_related("delivery_unit", "material")
            search_service = SearchService(self.request, self.active_fields)
            sorting_service = SortingService(self.request, self.active_fields)

            queryset = search_service.apply_search(queryset)
            queryset = sorting_service.apply_sorting(queryset)

            self._queryset = queryset
        return self._queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["search_query"] = self.request.GET.get("search", "")
        context["delivery_types"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES
        context["selected_menu"] = "unload_list"

        return context
