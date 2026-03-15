from django.db.models import Prefetch
from django.views.generic import ListView

from warenwirtschaft.models.material import Material
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.services.search_service import SearchableListViewMixin


class RecyclingListView(SearchableListViewMixin, ListView):
    model = Recycling
    template_name = "recycling/recycling_list.html"
    context_object_name = "recycling"
    paginate_by = 28

    field_configs = [
        {"field": "unloads__id", "label": "VID", "type": "text", "lookup": "exact"},
        {"field": "id", "label": "ZID", "type": "text", "lookup": "exact"},
        {"field": "created_at", "label": "Erstellt am", "type": "date"},
        {"field": "inactive_at", "label": "Erledigt am", "type": "date"},
        {
            "field": "status",
            "label": "Status",
            "type": "choice",
            "choices": lambda: Recycling._meta.get_field("status").choices,
        },
        {
            "field": "box_type",
            "label": "Behälter",
            "type": "choice",
            "choices": lambda: Recycling._meta.get_field("box_type").choices,
        },
        {
            "field": "material__name",
            "label": "Material",
            "type": "choice",
            "filter_field": "material_id",
            "choices": lambda: Material.objects.filter(recycling=True).order_by("name").values_list("id", "name"),
        },
        {"field": "weight", "label": "Gewicht (kg)", "type": "text", "lookup": "exact"},
        {"field": "barcode", "label": "Barcode", "type": "text", "lookup": "icontains"},
        {"field": "note", "label": "Anmerkung", "type": "text", "lookup": "icontains"},
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

        return self.apply_search_and_sort(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_type"] = Recycling.box_type
        context["selected_menu"] = "recycling_list"
        context["dashboard"] = True
        return context
