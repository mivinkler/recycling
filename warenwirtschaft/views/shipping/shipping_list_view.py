from django.views.generic import ListView
from django.db.models import Prefetch
from warenwirtschaft.models import Shipping, Unload, Recycling
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

        # Unload (Vorsortierung)
        ("unloads__material__name", "Material (Vorsort.)"),
        ("unloads__weight", "Gewicht (Vorsort.)"),
        ("unloads__box_type", "Behälter (Vorsort.)"),
        ("unloads__status", "Status (Vorsort.)"),

        # Recycling (Zerlegung)
        ("recyclings__material__name", "Material (Zerlegung)"),
        ("recyclings__weight", "Gewicht (Zerlegung)"),
        ("recyclings__box_type", "Behälter (Zerlegung)"),
        ("recyclings__status", "Status (Zerlegung)"),
    ]

    def get_queryset(self):
        unload_prefetch = Prefetch(
            "unloads",
            queryset=Unload.objects.select_related("material"),
        )
        recycling_prefetch = Prefetch(
            "recyclings",
            queryset=Recycling.objects.select_related("material"),
        )

        qs = (
            Shipping.objects
            .select_related("customer")
            .prefetch_related(unload_prefetch, recycling_prefetch)
        )

        fields = [field_name for field_name, _ in self.active_fields]

        choices_fields = {
            "transport": Shipping.transport,
            "unloads__box_type": Unload.box_type,
            "recyclings__box_type": Recycling.box_type,
            "unloads__status": Unload.status,
            "recyclings__status": Recycling.status,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        qs = search_service.apply_search(qs)
        qs = sorting_service.apply_sorting(qs)

        # distinct zur Sicherheit (SearchService/SortingService)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_obj = context["page_obj"]

        # Eine Zeile für Unload und Recycling
        rows = []
        for shipping in page_obj:
            for unload in shipping.unloads.all():
                rows.append({
                    "shipping": shipping,
                    "item": unload,
                    "kind": "unload",
                })

            for recycling in shipping.recyclings.all():
                rows.append({
                    "shipping": shipping,
                    "item": recycling,
                    "kind": "recycling",
                })

        context["rows"] = rows

        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")

        context["transport_choices"] = Shipping.transport
        context["unload_box_type_choices"] = Unload.box_type
        context["unload_status_choices"] = Unload.status
        context["recycling_box_type_choices"] = Recycling.box_type
        context["recycling_status_choices"] = Recycling.status

        context["selected_menu"] = "shipping_list"
        context["dashboard"] = True

        return context
