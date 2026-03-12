from django.views.generic import ListView
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService


class DeliveryListView(ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_list.html"
    context_object_name = "delivery_units"
    paginate_by = 28

    active_fields = [
        ("id", "LID"),
        ("delivery__id", "EID"),
        ("delivery__customer__name", "Kunde"),
        ("delivery__delivery_receipt", "Lieferschein"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("status", "Status"),
        ("created_at", "Erstellt am"),
        ("inactive_at", "Erledigt am"),
        ("barcode", "Barcode"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        queryset = (super().get_queryset().select_related("delivery", "delivery__customer", "material"))
        fields = [field[0] for field in self.active_fields]

        choices_fields = {
            "box_type": DeliveryUnit._meta.get_field("box_type").choices,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['request'] = self.request
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["box_types"] = DeliveryUnit.box_type
        context["selected_menu"] = "delivery_list"
        context["dashboard"] = True

        # context["filters"] = {
        #     "search": self.request.GET.get("search", ""),
        #     "date_start": self.request.GET.get("date_start", "")[:10],
        #     "date_end": self.request.GET.get("date_end", "")[:10],
        # }

        return context
