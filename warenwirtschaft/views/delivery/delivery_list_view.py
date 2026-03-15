from django.views.generic import ListView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.material import Material
from warenwirtschaft.services.search_service import SearchableListViewMixin


class DeliveryListView(SearchableListViewMixin, ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_list.html"
    context_object_name = "delivery_units"
    paginate_by = 28

    field_configs = [
        {"field": "delivery__id", "label": "LID", "type": "text", "lookup": "exact"},
        {"field": "id", "label": "EID", "type": "text", "lookup": "exact"},
        {"field": "created_at", "label": "Erstellt am", "type": "date"},
        {"field": "inactive_at", "label": "Erledigt am", "type": "date"},
        {
            "field": "status",
            "label": "Status",
            "type": "choice",
            "choices": lambda: DeliveryUnit._meta.get_field("status").choices,
        },
        {
            "field": "delivery__customer__name",
            "label": "Kunde",
            "type": "choice",
            "filter_field": "delivery__customer_id",
            "choices": lambda: Customer.objects.order_by("name").values_list("id", "name"),
        },
        {
            "field": "delivery__delivery_receipt",
            "label": "Lieferschein",
            "type": "text",
            "lookup": "icontains",
        },
        {
            "field": "box_type",
            "label": "Behälter",
            "type": "choice",
            "choices": lambda: DeliveryUnit._meta.get_field("box_type").choices,
        },
        {
            "field": "material__name",
            "label": "Material",
            "type": "choice",
            "filter_field": "material_id",
            "choices": lambda: Material.objects.filter(delivery=True).order_by("name").values_list("id", "name"),
        },
        {"field": "weight", "label": "Gewicht (kg)", "type": "text", "lookup": "exact"},
        {"field": "barcode", "label": "Barcode", "type": "text", "lookup": "icontains"},
        {"field": "note", "label": "Anmerkung", "type": "text", "lookup": "icontains"},
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
