from django.shortcuts import render
from django.views.generic import ListView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.services.search_service import SearchableListViewMixin


class CustomerListView(SearchableListViewMixin, ListView):
    model = Customer
    template_name = "customer/customer_list.html"
    context_object_name = "customers"
    paginate_by = 28

    field_configs = [
        {"field": "id", "label": "ID", "type": "text", "lookup": "exact"},
        {"field": "created_at", "label": "Datum", "type": "date"},
        {"field": "avv_number", "label": "AVV", "type": "text", "lookup": "exact"},
        {"field": "name", "label": "Lieferant", "type": "text", "lookup": "icontains"},
        {"field": "street", "label": "Straße", "type": "text", "lookup": "icontains"},
        {"field": "postal_code", "label": "PLZ", "type": "text", "lookup": "icontains"},
        {"field": "city", "label": "Stadt", "type": "text", "lookup": "icontains"},
        {"field": "phone", "label": "Telefon", "type": "text", "lookup": "icontains"},
        {"field": "email", "label": "Email", "type": "text", "lookup": "icontains"},
        {"field": "note", "label": "Anmerkung", "type": "text", "lookup": "icontains"},
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
