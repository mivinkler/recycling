from django.shortcuts import render
from django.views.generic import ListView
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService
from warenwirtschaft.models.customer import Customer

class CustomerListView(ListView):
    model = Customer
    template_name = "customer/customer_list.html"
    context_object_name = "customers"
    paginate_by = 28

    active_fields = [
        ("id", "ID"),
        ("avv_number", "AVV-Nummer"),
        ("name", "Kunde"),
        ("street", "Straße"),
        ("postal_code", "PLZ"),
        ("city", "Stadt"),
        ("phone", "Telefon"),
        ("email", "Email"),
        ("created_at", "Datum"),
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

    def dashboard(request):
        return render(request, 'dashboard.html', {'show_dashboard_menu': True})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj

        context["active_fields"] = self.active_fields
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["selected_menu"] = "customer_list"
        context["dashboard"] = True

        return context

