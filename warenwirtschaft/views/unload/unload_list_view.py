from django.db.models import Prefetch
from django.views.generic import ListView

from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.search_service import (
    SearchableListViewMixin,
    barcode_filter,
    box_type_filter,
    choice_filter,
    created_at_filter,
    id_filter,
    inactive_at_filter,
    material_filter,
    note_filter,
    weight_filter,
)


UNLOAD_LIST_STATUS_CHOICES = [
    (value, label)
    for value, label in StatusChoices.CHOICES
    if value != StatusChoices.WARTET_AUF_VORSORTIERUNG
]


class UnloadListView(SearchableListViewMixin, ListView):
    model = Unload
    template_name = "unload/unload_list.html"
    context_object_name = "unloads"
    paginate_by = 28

    field_configs = [
        id_filter("delivery_units__id", "EID"),
        id_filter("id", "VID"),
        created_at_filter(label="Erstellt am"),
        inactive_at_filter(),
        choice_filter("status", "Status", lambda: UNLOAD_LIST_STATUS_CHOICES),
        box_type_filter(Unload),
        material_filter(lambda: Material.objects.filter(unload=True)),
        weight_filter(),
        barcode_filter(),
        note_filter(),
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

        return self.apply_search_and_sort(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_type"] = Unload.box_type
        context["selected_menu"] = "unload_list"
        context["dashboard"] = True
        return context
