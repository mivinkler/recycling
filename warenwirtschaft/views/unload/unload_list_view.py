from django.db.models import Prefetch
from django.views.generic import ListView

from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.list_view_service import ListViewService


UNLOAD_LIST_STATUS_CHOICES = [
    (value, label)
    for value, label in StatusChoices.CHOICES
    if value != StatusChoices.WARTET_AUF_VORSORTIERUNG
]


class UnloadListView(ListViewService, ListView):
    model = Unload
    template_name = "unload/unload_list.html"
    context_object_name = "unloads"
    paginate_by = 28

    field_configs = [
        {"field": "delivery_units__id", "label": "EID", "lookup": "exact"},
        {"field": "id", "label": "VID", "lookup": "exact"},
        {"field": "barcode", "label": "Barcode"},
        {"field": "created_at", "label": "Erstellt am", "type": "date"},
        {"field": "inactive_at", "label": "Erledigt am", "type": "date"},
        {
            "field": "status",
            "label": "Status",
            "type": "choice",
            "choices": lambda: UNLOAD_LIST_STATUS_CHOICES,
        },
        {
            "field": "box_type",
            "label": "Behälter",
            "type": "choice",
            "choices": Unload._meta.get_field("box_type").choices,
        },
        {
            "field": "material__name",
            "label": "Material",
            "type": "choice",
            "filter_field": "material_id",
            "choices": lambda: Material.for_section("unload").order_by("name").values_list("id", "name"),
        },
        {"field": "weight", "label": "Gewicht (kg)", "lookup": "exact"},
        {"field": "note", "label": "Anmerkung"},
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
