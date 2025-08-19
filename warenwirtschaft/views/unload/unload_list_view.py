from django.views.generic import ListView
from django.db.models import Prefetch
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class UnloadListView(ListView):
    model = Unload
    template_name = "unload/unload_list.html"
    context_object_name = "unloads"
    paginate_by = 22

    # DE: Nach M2M-Umstellung auf delivery_units__...
    active_fields = [
        ("id", "ID"),
        ("delivery_units__delivery__id", "LD"),
        ("delivery_units__id", "LED"),
        ("delivery_units__delivery__supplier__name", "Lieferant"),
        ("box_type", "Behälter"),
        ("material__name", "Material"),
        ("weight", "Gewicht"),
        ("status", "Status"),
        ("created_at", "Datum"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        # DE: Prefetch für M2M; select_related geht hier nicht
        qs = (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "delivery_units",
                    queryset=DeliveryUnit.objects.select_related("delivery__supplier"),
                )
            )
        )

        fields = [f[0] for f in self.active_fields]
        choices_fields = {
            "box_type": Unload.BOX_TYPE_CHOICES,
            "status": Unload.STATUS_CHOICES,
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        qs = search_service.apply_search(qs)
        qs = sorting_service.apply_sorting(qs)

        # DE: M2M-Joins können Duplikate erzeugen → distinct()
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())
        context["page_obj"] = page_obj
        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["box_type"] = Unload.BOX_TYPE_CHOICES
        context["status"] = Unload.STATUS_CHOICES
        context["selected_menu"] = "unload_list"
        context["dashboard"] = True
        return context
