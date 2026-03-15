from django.shortcuts import render
from django.views.generic import ListView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.services.search_service import (
    SearchableListViewMixin,
    created_at_filter,
    id_filter,
    note_filter,
    text_filter,
)


class CustomerListView(SearchableListViewMixin, ListView):
    model = Customer
    template_name = "customer/customer_list.html"
    context_object_name = "customers"
    paginate_by = 28

    field_configs = [
        id_filter(),
        created_at_filter(),
        id_filter("avv_number", "AVV"),
        text_filter("name", "Lieferant"),
        text_filter("street", "Stra\u00dfe"),
        text_filter("postal_code", "PLZ"),
        text_filter("city", "Stadt"),
        text_filter("phone", "Telefon"),
        text_filter("email", "Email"),
        note_filter(),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.apply_search_and_sort(queryset)

    def dashboard(request):
        return render(request, "dashboard.html", {"show_dashboard_menu": True})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_menu"] = "customer_list"
        context["dashboard"] = True
        return context
