from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from warenwirtschaft.models import Supplier

class SupplierListView(ListView):
    model = Supplier
    template_name = "supplier/supplier_list.html"
    context_object_name = "suppliers"
    paginate_by = 20

    active_fields= ["id", "avv_number", "name", "street", "postal_code", "city", "phone", "email", "note"]
    sort_mapping = {field: field for field in active_fields}
    sort_mapping.update({f"{key}_desc": f"-{val}" for key, val in sort_mapping.items()})

    def apply_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip()
        if not search_query:
            return queryset

        q_objects = Q()
        for field in self.active_fields:
            lookup = f"{field}__icontains"
            q_objects |= Q(**{lookup: search_query})

        return queryset.filter(q_objects)

    def apply_sorting(self, queryset):
        sort_param = self.request.GET.get("sort", "id_asc")  # Voreingestellte Sortierung nach id_asc
        sort_field = sort_param.replace("_asc", "").replace("_desc", "")  # Entfern von _asc/_desc

        if sort_param.endswith("_desc"):
            sort_field = f"-{sort_field}"

        return queryset.order_by(sort_field)

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.apply_sorting(self.apply_search(queryset))

    def get_paginated_queryset(self, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.get_queryset()
        context["page_obj"] = self.get_paginated_queryset(filtered_queryset)
        context["search_query"] = self.request.GET.get("search", "")
        return context
