from django.views.generic import ListView
from django.db.models import Prefetch
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService

class RecyclingListView(ListView):
    model = Recycling
    template_name = "recycling/recycling_list.html"
    context_object_name = "recycling"
    paginate_by = 28

    active_fields = [
        ("id", "ID"),
        ("unloads__id", "VID"),
        ("status", "Status"),
        ("box_type", "Behälter"),
        ("weight", "Gewicht"),
        ("material__name", "Material"),
        ("created_at", "Erstellt am"),
        ("inactive_at", "Erledigt am"),
        ("barcode", "Barcode"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        unloads_prefetch = Prefetch(
            "unloads",
            queryset=Unload.objects.select_related("material"),
        )

        queryset = (
            super()
            .get_queryset()
            .select_related("material")
            .prefetch_related(unloads_prefetch)
        )

        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "box_type": Recycling._meta.get_field("box_type").choices,
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
        context["box_type"] = Recycling.box_type
        context["selected_menu"] = "recycling_list"
        context["dashboard"] = True

        return context
