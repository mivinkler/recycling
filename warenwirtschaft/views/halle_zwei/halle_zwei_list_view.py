from django.views.generic import ListView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.halle_zwei import HalleZwei
from warenwirtschaft.models.material import Material
from warenwirtschaft.services.search_service import SearchableListViewMixin


class HalleZweiListView(SearchableListViewMixin, ListView):
    model = HalleZwei
    template_name = "halle_zwei/halle_zwei_list.html"
    context_object_name = "halle-zwei"
    paginate_by = 28

    field_configs = [
        {"field": "delivery_unit__id", "label": "EID", "type": "text", "lookup": "exact"},
        {"field": "id", "label": "HID", "type": "text", "lookup": "exact"},
        {
            "field": "delivery_unit__delivery__customer__name",
            "label": "Kunde",
            "type": "choice",
            "filter_field": "delivery_unit__delivery__customer_id",
            "choices": lambda: Customer.objects.order_by("name").values_list("id", "name"),
        },
        {"field": "created_at", "label": "Erstellt am", "type": "date"},
        {"field": "inactive_at", "label": "Erledigt am", "type": "date"},
        {
            "field": "delivery_unit__box_type",
            "label": "Behälter",
            "type": "choice",
            "choices": lambda: DeliveryUnit._meta.get_field("box_type").choices,
        },
        {
            "field": "delivery_unit__material__name",
            "label": "Material",
            "type": "choice",
            "filter_field": "delivery_unit__material_id",
            "choices": lambda: Material.objects.filter(halle_zwei=True).order_by("name").values_list("id", "name"),
        },
        {"field": "delivery_unit__weight", "label": "Gewicht (kg)", "type": "text", "lookup": "exact"},
        {"field": "delivery_unit__barcode", "label": "Barcode", "type": "text", "lookup": "icontains"},
        {"field": "delivery_unit__note", "label": "Anmerkung", "type": "text", "lookup": "icontains"},
    ]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related(
                "delivery_unit",
                "delivery_unit__delivery",
                "delivery_unit__delivery__customer",
                "delivery_unit__material",
                "shipping",
            )
        )
        return self.apply_search_and_sort(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_menu"] = "halle_zwei_list"
        context["dashboard"] = True
        return context
