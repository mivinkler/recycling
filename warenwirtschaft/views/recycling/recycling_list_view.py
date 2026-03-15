from django.db.models import Prefetch
from django.views.generic import ListView

from warenwirtschaft.models.material import Material
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.services.search_service import (
    SearchableListViewMixin,
    barcode_filter,
    box_type_filter,
    created_at_filter,
    id_filter,
    inactive_at_filter,
    material_filter,
    note_filter,
    status_filter,
    weight_filter,
)


class RecyclingListView(SearchableListViewMixin, ListView):
    model = Recycling
    template_name = "recycling/recycling_list.html"
    context_object_name = "recycling"
    paginate_by = 28

    field_configs = [
        id_filter("unloads__id", "VID"),
        id_filter("id", "ZID"),
        created_at_filter(label="Erstellt am"),
        inactive_at_filter(),
        status_filter(Recycling),
        box_type_filter(Recycling),
        material_filter(lambda: Material.objects.filter(recycling=True)),
        weight_filter(),
        barcode_filter(),
        note_filter(),
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
