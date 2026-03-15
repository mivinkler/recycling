from django.db.models import Prefetch
from django.views.generic import ListView

from warenwirtschaft.models import HalleZwei, Recycling, Shipping, Unload
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.services.search_service import SearchableListViewMixin


class ShippingListView(SearchableListViewMixin, ListView):
    model = Shipping
    template_name = "shipping/shipping_list.html"
    context_object_name = "shippings"
    paginate_by = 28
    search_distinct = True

    field_configs = [
        {"field": "id", "label": "ID", "type": "text", "lookup": "exact"},
        {"field": "created_at", "label": "Datum", "type": "date"},
        {
            "field": "customer__name",
            "label": "Abholer",
            "type": "choice",
            "filter_field": "customer_id",
            "choices": lambda: Customer.objects.order_by("name").values_list("id", "name"),
        },
        {"field": "certificate", "label": "Übernahmeschein", "type": "text", "lookup": "exact"},
        {
            "field": "transport",
            "label": "Transport",
            "type": "choice",
            "choices": lambda: Shipping._meta.get_field("transport").choices,
        },
        {"field": "note", "label": "Notiz", "type": "text", "lookup": "icontains"},
    ]

    def get_queryset(self):
        unload_prefetch = Prefetch(
            "unloads",
            queryset=Unload.objects.all().order_by("pk"),
        )
        recycling_prefetch = Prefetch(
            "recyclings",
            queryset=Recycling.objects.all().order_by("pk"),
        )
        halle_zwei_prefetch = Prefetch(
            "halle_zwei",
            queryset=HalleZwei.objects.all().order_by("pk"),
        )

        queryset = (
            super()
            .get_queryset()
            .select_related("customer")
            .prefetch_related(
                unload_prefetch,
                recycling_prefetch,
                halle_zwei_prefetch,
            )
        )

        return self.apply_search_and_sort(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transport_choices"] = Shipping._meta.get_field("transport").choices
        context["selected_menu"] = "shipping_list"
        context["dashboard"] = True
        return context
