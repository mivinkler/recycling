from django.views.generic import ListView
from django.db.models import Prefetch
from warenwirtschaft.models import Shipping, Unload, Recycling
from warenwirtschaft.services.pagination_service import PaginationService
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService


class ShippingListView(ListView):
    model = Shipping
    template_name = "shipping/shipping_list.html"
    context_object_name = "shippings"
    paginate_by = 28

    # ---- Aktive Felder für Suche und Sortierung ----
    # (Feldname, Spaltenüberschrift)
    active_fields = [
        ("id", "LID"),
        ("customer__name", "Abholer"),
        ("certificate", "Begleitschein"),
        ("note", "Anmerkung"),
        ("created_at", "Datum"),
        ("transport", "Transport"),

        # Felder aus Unload (Vorsortierung)
        ("unload_for_shipping__material__name", "Material (Vorsort.)"),
        ("unload_for_shipping__weight", "Gewicht (Vorsort.)"),
        ("unload_for_shipping__box_type", "Behälter (Vorsort.)"),
        ("unload_for_shipping__status", "Status (Vorsort.)"),

        # Felder aus Recycling (Aufbereitung)
        ("recycling_for_shipping__material__name", "Material (Aufbereitung)"),
        ("recycling_for_shipping__weight", "Gewicht (Aufbereitung)"),
        ("recycling_for_shipping__box_type", "Behälter (Aufbereitung)"),
        ("recycling_for_shipping__status", "Status (Aufbereitung)"),
    ]

    def get_queryset(self):
        """
        Erstellt das Basis-QuerySet für Shipping inklusive Prefetches
        und wendet Suche/Sortierung über die Services an.
        """
        # ---- Basis-QuerySet mit Prefetches für bessere Performance ----
        unload_prefetch = Prefetch(
            "unload_for_shipping",
            queryset=Unload.objects.select_related("material"),
        )
        recycling_prefetch = Prefetch(
            "recycling_for_shipping",
            queryset=Recycling.objects.select_related("material"),
        )

        queryset = (
            Shipping.objects
            .select_related("customer")
            .prefetch_related(unload_prefetch, recycling_prefetch)
        )

        # Nur die Feldnamen für Search/Sorting extrahieren
        fields = [field_name for field_name, _ in self.active_fields]

        # ---- Auswahlfelder für die Suche (Choice-Felder) ----
        choices_fields = {
            "transport": Shipping.TRANSPORT_CHOICES,
            "unload_for_shipping__box_type": Unload.BOX_TYPE_CHOICES,
            "recycling_for_shipping__box_type": Recycling.BOX_TYPE_CHOICES,
            "unload_for_shipping__status": Unload.STATUS_CHOICES,
            "recycling_for_shipping__status": Recycling.STATUS_CHOICES,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        # distinct(), falls durch Joins/Prefetch Duplikate entstehen könnten
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        """
        Ergänzt den Kontext um Pagination, aktive Felder und Such-/Sortierparameter.
        """
        context = super().get_context_data(**kwargs)

        # ---- Eigene Pagination über PaginationService ----
        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["active_fields"] = self.active_fields

        # ---- Such- und Sortierparameter an Template übergeben ----
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")

        # ---- Choice-Listen für Filter/Anzeige im Template ----
        context["transport_choices"] = Shipping.TRANSPORT_CHOICES
        context["unload_box_type_choices"] = Unload.BOX_TYPE_CHOICES
        context["unload_status_choices"] = Unload.STATUS_CHOICES
        context["recycling_box_type_choices"] = Recycling.BOX_TYPE_CHOICES
        context["recycling_status_choices"] = Recycling.STATUS_CHOICES

        # ---- UI-Status ----
        context["selected_menu"] = "shipping_list"
        context["dashboard"] = True

        return context
