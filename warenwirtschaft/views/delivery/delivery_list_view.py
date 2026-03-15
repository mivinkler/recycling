from django.views.generic import ListView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.delivery_unit import DeliveryUnit
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
    status_filter,
    text_filter,
    weight_filter,
)


class DeliveryListView(SearchableListViewMixin, ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_list.html"
    context_object_name = "delivery_units"
    paginate_by = 28

    field_configs = [
        id_filter("delivery__id", "LID"),
        id_filter("id", "EID"),
        created_at_filter(label="Erstellt am"),
        inactive_at_filter(),
        status_filter(DeliveryUnit),
        customer_filter(
            lambda: Customer.objects.all(),
            field="delivery__customer__name",
            filter_field="delivery__customer_id",
        ),
        text_filter("delivery__delivery_receipt", "Lieferschein"),
        box_type_filter(DeliveryUnit),
        material_filter(lambda: Material.objects.filter(delivery=True)),
        weight_filter(),
        barcode_filter(),
        note_filter(),
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
