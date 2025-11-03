from django.views.generic import ListView
from django.db.models import Q
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService
from warenwirtschaft.models import Recycling, Unload, Shipping

class ShippingListView(ListView):
    model = Shipping
    template_name = "shipping/shipping_list.html"
    context_object_name = "shippings"
    paginate_by = 28

    #  Für Suche und Sortierung
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
    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer")

        fields = [field[0] for field in self.active_fields]

        # Choice-Felder kommen NICHT aus Shipping, sondern aus Recycling und Unload
        choices_fields = {
            "recycling__box_type": dict(Recycling.BOX_TYPE_CHOICES),
            "unload__box_type": dict(Unload.BOX_TYPE_CHOICES),

            "recycling__status": dict(Recycling.STATUS_CHOICES),
            "unload__status": dict(Unload.STATUS_CHOICES),
        }

        # s.a. Services
        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        # DISTINCT, weil mehrere Recycling/Unload-Einträge sonst mehrere Zeilen erzeugen
        queryset = queryset.distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # s.a. Services
        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.object_list)

        context["page_obj"] = page_obj
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["selected_menu"] = "shipping_list"
        context["dashboard"] = True

        # Choices
        context["box_types_rec"] = Recycling.BOX_TYPE_CHOICES
        context["box_types_unl"] = Unload.BOX_TYPE_CHOICES
        context["status_rec"] = Recycling.STATUS_CHOICES
        context["status_unl"] = Unload.STATUS_CHOICES

        return context
