from django.views.generic import ListView
from warenwirtschaft.models import Shipping, Recycling, Unload
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class ShippingListView(ListView):
    model = Shipping
    template_name = "shipping/shipping_list.html"
    context_object_name = "shippings"
    paginate_by = 28

    # ---- Aktive Felder für Suche und Sortierung ----
    active_fields = [
        ("id", "LID"),
        ("customer__name", "Abholer"),
        ("certificate", "Begleitschein"),
        ("note", "Anmerkung"),
        ("created_at", "Datum"),

        # Verbundene Felder aus Recycling und Unload
        ("recycling__box_type", "Behälter (Aufbereitung)"),
        ("unload__box_type", "Behälter (Vorsort.)"),

        ("recycling__material__name", "Material (Aufbereitung)"),
        ("unload__material__name", "Material (Vorsort.)"),

        ("recycling__weight", "Gewicht (Aufbereitung)"),
        ("unload__weight", "Gewicht (Vorsort.)"),

        ("recycling__status", "Status (Aufbereitung)"),
        ("unload__status", "Status (Vorsort.)"),

        ("transport", "Transportart"),
    ]

    def get_queryset(self):
        # Vorladen aller benötigten Beziehungen
        queryset = (
            super()
            .get_queryset()
            .select_related(
                "customer",
                "recycling", "recycling__material",
                "unload", "unload__material",
            )
        )

        fields = [f for f, _ in self.active_fields]

        # CHOICES aus verknüpften Modellen für Suchservice
        choices_fields = {
            "recycling__box_type": dict(Recycling.BOX_TYPE_CHOICES),
            "unload__box_type": dict(Unload.BOX_TYPE_CHOICES),
            "recycling__status": dict(Recycling.STATUS_CHOICES),
            "unload__status": dict(Unload.STATUS_CHOICES),
            "transport": dict(Shipping.TRANSPORT_CHOICES),
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.object_list)

        context.update({
            "page_obj": page_obj,
            "active_fields": self.active_fields,
            "search_query": self.request.GET.get("search", ""),
            "sort_param": self.request.GET.get("sort", ""),
            "selected_menu": "shipping_list",
            "dashboard": True,

            # Für Dropdowns oder Filter im Template
            "box_types_rec": Recycling.BOX_TYPE_CHOICES,
            "box_types_unl": Unload.BOX_TYPE_CHOICES,
            "status_rec": Recycling.STATUS_CHOICES,
            "status_unl": Unload.STATUS_CHOICES,
            "transport_choices": Shipping.TRANSPORT_CHOICES,
        })
        return context
