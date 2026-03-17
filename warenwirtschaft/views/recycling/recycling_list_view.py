from django.db.models import Prefetch
from django.views.generic import ListView

from warenwirtschaft.forms.recycling_form import (
    RECYCLING_FORM_BOX_TYPE_CHOICES,
    RECYCLING_FORM_STATUS_CHOICES,
)
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.list_view_service import ListViewService


RECYCLING_LIST_STATUS_CHOICES = [
    *RECYCLING_FORM_STATUS_CHOICES,
    (StatusChoices.ERLEDIGT, "Erledigt"),
]

RECYCLING_LIST_BOX_TYPE_CHOICES = list(RECYCLING_FORM_BOX_TYPE_CHOICES)


class RecyclingListView(ListViewService, ListView):
    model = Recycling
    template_name = "recycling/recycling_list.html"
    context_object_name = "recycling"
    paginate_by = 28

    field_configs = [
        {"field": "unloads__id", "label": "VID", "lookup": "exact"},
        {"field": "id", "label": "ZID", "lookup": "exact"},
        {"field": "barcode", "label": "Barcode"},
        {"field": "created_at", "label": "Erstellt am", "type": "date"},
        {"field": "inactive_at", "label": "Erledigt am", "type": "date"},
        {
            "field": "status",
            "label": "Status",
            "type": "choice",
            "choices": lambda: RECYCLING_LIST_STATUS_CHOICES,
        },
        {
            "field": "box_type",
            "label": "Behälter",
            "type": "choice",
            "choices": lambda: RECYCLING_LIST_BOX_TYPE_CHOICES,
        },
        {
            "field": "material__name",
            "label": "Material",
            "type": "choice",
            "filter_field": "material_id",
            "choices": lambda: Material.for_section("recycling").order_by("name").values_list("id", "name"),
        },
        {"field": "weight", "label": "Gewicht (kg)", "lookup": "exact"},
        {"field": "note", "label": "Anmerkung"},
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
