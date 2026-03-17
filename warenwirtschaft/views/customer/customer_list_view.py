from django.shortcuts import render
from django.views.generic import ListView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.services.list_view_service import ListViewService


class CustomerListView(ListViewService, ListView):
    model = Customer
    template_name = "customer/customer_list.html"
    context_object_name = "customers"
    paginate_by = 28

    field_configs = [
        {"field": "id", "label": "ID", "lookup": "exact"},
        {"field": "created_at", "label": "Datum", "type": "date"},
        {"field": "avv_number", "label": "AVV", "lookup": "exact"},
        {"field": "name", "label": "Lieferant"},
        {"field": "street", "label": "Straße"},
        {"field": "postal_code", "label": "PLZ"},
        {"field": "city", "label": "Stadt"},
        {"field": "phone", "label": "Telefon"},
        {"field": "email", "label": "Email"},
        {"field": "note", "label": "Anmerkung"},
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
