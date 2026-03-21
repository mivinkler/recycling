from django.views.generic import ListView

from warenwirtschaft.forms.delivery_form import (
    DELIVERY_FORM_B2B_CHOICES,
    DELIVERY_UNIT_FORM_STATUS_CHOICES,
)
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.material import Material
from warenwirtschaft.services.list_view_service import ListViewService


class DeliveryListView(ListViewService, ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_list.html"
    context_object_name = "delivery_units"
    paginate_by = 28

    field_configs = [
        {"field": "delivery__id", "label": "LID", "lookup": "exact"},
        {"field": "id", "label": "EID", "lookup": "exact"},
        {"field": "barcode", "label": "Barcode"},
        {"field": "created_at", "label": "Erstellt am", "type": "date"},
        {"field": "inactive_at", "label": "Erledigt am", "type": "date"},
        {
            "field": "status",
            "label": "Status",
            "type": "choice",
            "choices": lambda: DELIVERY_UNIT_FORM_STATUS_CHOICES,
        },
        {
            "field": "delivery__customer__name",
            "label": "Kunde",
            "type": "choice",
            "filter_field": "delivery__customer_id",
            "choices": lambda: Customer.objects.order_by("name").values_list("id", "name"),
        },
        {"field": "delivery__delivery_receipt", "label": "Lieferschein"},
        {
            "field": "box_type",
            "label": "Behälter",
            "type": "choice",
            "choices": DeliveryUnit._meta.get_field("box_type").choices,
        },
        {
            "field": "delivery__b2b",
            "label": "B2B",
            "type": "choice",
            "choices": lambda: DELIVERY_FORM_B2B_CHOICES,
        },
        {
            "field": "material__name",
            "label": "Material",
            "type": "choice",
            "filter_field": "material_id",
            "choices": lambda: Material.for_section("delivery").order_by("name").values_list("id", "name"),
        },
        {"field": "weight", "label": "Gewicht (kg)", "lookup": "exact"},
        {"field": "note", "label": "Anmerkung"},
    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("delivery", "delivery__customer", "material")
        return self.apply_search_and_sort(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_types"] = DeliveryUnit.box_type
        context["selected_menu"] = "delivery_list"
        context["dashboard"] = True
        return context
