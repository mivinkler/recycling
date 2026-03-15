from django.views.generic import ListView

from warenwirtschaft.models import BarcodeGenerator
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.material import Material
from warenwirtschaft.services.search_service import SearchableListViewMixin


class BarcodeGeneratorListView(SearchableListViewMixin, ListView):
    model = BarcodeGenerator
    template_name = "barcode/barcode_generator_list.html"
    context_object_name = "barcodes"
    paginate_by = 28

    field_configs = [
        {"field": "id", "label": "ID", "type": "text", "lookup": "exact"},
        {"field": "created_at", "label": "Datum", "type": "date"},
        {"field": "barcode", "label": "Barcode", "type": "text", "lookup": "icontains"},
        {
            "field": "transport",
            "label": "Transport",
            "type": "choice",
            "choices": lambda: BarcodeGenerator._meta.get_field("transport").choices,
        },
        {
            "field": "customer__name",
            "label": "Customer",
            "type": "choice",
            "filter_field": "customer_id",
            "choices": lambda: Customer.objects.order_by("name").values_list("id", "name"),
        },
        {
            "field": "box_type",
            "label": "Behälter",
            "type": "choice",
            "choices": lambda: BarcodeGenerator._meta.get_field("box_type").choices,
        },
        {
            "field": "material__name",
            "label": "Material",
            "type": "choice",
            "filter_field": "material_id",
            "choices": lambda: Material.objects.order_by("name").values_list("id", "name"),
        },
        {"field": "receipt", "label": "Lieferschein", "type": "text", "lookup": "icontains"},
    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer", "material")
        return self.apply_search_and_sort(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_menu"] = "barcode_generator_list"
        context["dashboard"] = True
        return context
