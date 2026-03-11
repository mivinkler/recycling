from django.views.generic import ListView
from django.db.models import Prefetch

from warenwirtschaft.models import Shipping, Unload, Recycling, HalleZwei
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService


class ShippingListView(ListView):
    model = Shipping
    template_name = "shipping/shipping_list.html"
    context_object_name = "shippings"
    paginate_by = 28

    active_fields = [
        ("id", "LID"),
        ("customer__name", "Abholer"),
        ("certificate", "Begleitschein"),
        ("note", "Anmerkung"),
        ("created_at", "Datum"),
        ("transport", "Transport"),
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

        fields = [field_name for field_name, _ in self.active_fields]

        choices_fields = {
            "transport": Shipping._meta.get_field("transport").choices,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        # distinct zur Sicherheit bei Suche und Sortierung
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["transport_choices"] = Shipping._meta.get_field("transport").choices
        context["selected_menu"] = "shipping_list"
        context["dashboard"] = True

        return context