from django.views.generic import ListView
from warenwirtschaft.models import Supplier
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class SupplierListView(ListView):
    model = Supplier
    template_name = "supplier/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 22

    active_fields = [
        ("id", "ID"),
        ("avv_number", "AVV-Nummer"),
        ("name", "Lieferant"),
        ("street", "Straße"),
        ("postal_code", "PLZ"),
        ("city", "Stadt"),
        ("phone", "Telefon"),
        ("email", "Email"),
        ("created_at", "Erstellt am"),
        ("note", "Anmerkung"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]
        search_service = SearchService(self.request, fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["sort_param"] = self.request.GET.get("sort", "")
        context["search_query"] = self.request.GET.get("search", "")
        context["active_fields"] = self.active_fields

        context["selected_menu"] = "supplier_list"

        return context

