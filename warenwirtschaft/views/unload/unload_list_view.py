from django.views.generic import ListView
from django.db.models import Prefetch
from warenwirtschaft.models.delivery_unit import DeliveryUnit

from warenwirtschaft.models.unload import Unload
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService

class UnloadListView(ListView):
    model = Unload
    template_name = "unload/unload_list.html"
    context_object_name = "unloads"
    paginate_by = 28

    active_fields = [
        ("id", "Vorsortierung-ID"),
        ("status", "Status"),
        ("delivery_units__id", "Lieferung-ID"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("created_at", "Datum"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        delivery_units_prefetch = Prefetch(
            "delivery_units",
            queryset=DeliveryUnit.objects.select_related("delivery", "material"),
        )

        queryset = (
            super()
            .get_queryset()
            .select_related("material")
            .prefetch_related(delivery_units_prefetch)
        )

        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "box_type": Unload._meta.get_field("box_type").choices,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["box_type"] = Unload.box_type
        context["selected_menu"] = "unload_list"
        context["dashboard"] = True

        return context
