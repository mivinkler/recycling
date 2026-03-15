from django.views.generic import ListView

from warenwirtschaft.models import BarcodeGenerator
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.material import Material
from warenwirtschaft.services.search_service import (
    SearchableListViewMixin,
    barcode_filter,
    box_type_filter,
    created_at_filter,
    customer_filter,
    id_filter,
    material_filter,
    text_filter,
    transport_filter,
)


class BarcodeGeneratorListView(SearchableListViewMixin, ListView):
    model = BarcodeGenerator
    template_name = "barcode/barcode_generator_list.html"
    context_object_name = "barcodes"
    paginate_by = 28

    field_configs = [
        id_filter(),
        created_at_filter(),
        barcode_filter(),
        transport_filter(BarcodeGenerator),
        customer_filter(lambda: Customer.objects.all(), label="Customer"),
        box_type_filter(BarcodeGenerator),
        material_filter(lambda: Material.objects.all()),
        text_filter("receipt", "Lieferschein"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer", "material")
        return self.apply_search_and_sort(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_menu"] = "barcode_generator_list"
        context["dashboard"] = True
        return context
