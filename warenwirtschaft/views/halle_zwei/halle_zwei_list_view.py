from django.views.generic import ListView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.halle_zwei import HalleZwei
from warenwirtschaft.models.material import Material
from warenwirtschaft.services.search_service import (
    SearchableListViewMixin,
    barcode_filter,
    box_type_filter,
    created_at_filter,
    customer_filter,
    id_filter,
    inactive_at_filter,
    material_filter,
    note_filter,
    weight_filter,
)


class HalleZweiListView(SearchableListViewMixin, ListView):
    model = HalleZwei
    template_name = "halle_zwei/halle_zwei_list.html"
    context_object_name = "halle-zwei"
    paginate_by = 28

    field_configs = [
        id_filter("delivery_unit__id", "EID"),
        id_filter("id", "HID"),
        customer_filter(
            lambda: Customer.objects.all(),
            field="delivery_unit__delivery__customer__name",
            filter_field="delivery_unit__delivery__customer_id",
        ),
        created_at_filter(label="Erstellt am"),
        inactive_at_filter(),
        box_type_filter(DeliveryUnit, field="delivery_unit__box_type"),
        material_filter(
            lambda: Material.objects.filter(halle_zwei=True),
            field="delivery_unit__material__name",
            filter_field="delivery_unit__material_id",
        ),
        weight_filter("delivery_unit__weight"),
        barcode_filter("delivery_unit__barcode"),
        note_filter("delivery_unit__note"),
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
