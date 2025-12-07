from django.views.generic import ListView
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class DeliveryListView(ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_list.html"
    context_object_name = "delivery_units"
    paginate_by = 28

    active_fields = [
        ("delivery__id", "LID"),
        ("delivery__customer__name", "Kunde"),
        ("delivery__delivery_receipt", "Lieferschein"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("created_at", "Datum"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "box_type": DeliveryUnit.box_type,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context['request'] = self.request
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["box_types"] = DeliveryUnit.box_type
        context["selected_menu"] = "delivery_list"
        
        # Panel mit Suche und Sortierung
        context["dashboard"] = True

        context["filters"] = {
            "search": self.request.GET.get("search", ""),
            "date_start": self.request.GET.get("date_start", "")[:10],
            "date_end": self.request.GET.get("date_end", "")[:10],
        }

        return context
