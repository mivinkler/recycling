# Listenansicht für Abholungen mit Suche/Sortierung über verbundene Felder
from django.views.generic import ListView
from django.db.models import Q
from django.db.models import Sum, Min, Max  # optional für Annotationen
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService
from warenwirtschaft.models.shipping import Shipping
from warenwirtschaft.models import Recycling, Unload  # für CHOICES

class ShippingListView(ListView):
    model = Shipping
    template_name = "shipping/shipping_list.html"
    context_object_name = "shippings"  # Plural für Listenansicht
    paginate_by = 50

    # Sicht-/Suchfelder (Basis: Shipping + verbundene Modelle)
    # Achtung: Da 'model = Shipping' ist, bitte KEIN 'shipping__...' Präfix.
    active_fields = [
        ("id", "LID"),
        ("customer__name", "Abholer"),
        ("certificate", "Begleitschein"),
        ("note", "Anmerkung"),
        ("created_at", "Datum"),

        # Verbundene Felder aus Recycling/Unload (für Suche/Sortierung)
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
        # Basis-QuerySet
        queryset = super().get_queryset().select_related("customer")

        # Felder extrahieren
        fields = [field[0] for field in self.active_fields]

        # Choice-Felder kommen NICHT aus Shipping, sondern aus Recycling/Unload
        # Wenn beide Modelle identische Choices teilen, ist es okay die gleichen Mappings
        # zwei Mal zu hinterlegen (je Feldname).
        choices_fields = {
            "recycling__box_type": dict(Recycling.BOX_TYPE_CHOICES),
            "unload__box_type": dict(Unload.BOX_TYPE_CHOICES),

            "recycling__status": dict(Recycling.STATUS_CHOICES),
            "unload__status": dict(Unload.STATUS_CHOICES),
        }

        # Services anwenden (Suchen/Sortieren); DISTINCT gegen Duplikate durch JOINs
        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        # DISTINCT, weil mehrere Recycling/Unload-Einträge sonst mehrere Zeilen erzeugen
        queryset = queryset.distinct()

        # (Optional) Beispiel: Summen/Min/Max der Gewichte je Abholung anzeigen
        # queryset = queryset.annotate(
        #     total_weight_rec=Sum("recycling__weight"),
        #     total_weight_unl=Sum("unload__weight"),
        # )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Paginator über Service (verwendet das bereits gefilterte/sortierte QuerySet)
        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.object_list)

        # Kontext befüllen (ohne versehentliche Tupel durch trailing comma)
        context["page_obj"] = page_obj
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["selected_menu"] = "shipping_list"
        context["dashboard"] = True

        # Choices ggf. für Filter-UI im Template
        context["box_types_rec"] = Recycling.BOX_TYPE_CHOICES
        context["box_types_unl"] = Unload.BOX_TYPE_CHOICES
        context["status_rec"] = Recycling.STATUS_CHOICES
        context["status_unl"] = Unload.STATUS_CHOICES

        return context
