from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from warenwirtschaft.models import Supplier, Delivery
from django.db.models import Q


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = "supplier/supplier_detail.html"
    context_object_name = "supplier"
    paginate_by = 14
    
    search_fields = ["id", "units", "delivery_receipt", "weight", "delivery_date", "note"]
    sort_mapping = {
        "id": "id",
        "units": "units",
        "delivery_receipt": "delivery_receipt",
        "weight": "weight",
        "delivery_date": "delivery_date",
        "note": "note",
    }
    sort_mapping.update({f"{key}_desc": f"-{val}" for key, val in sort_mapping.items()})

    def apply_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip()
        if not search_query:
            return queryset
        
        q_objects = Q()
        for field in self.search_fields:
            lookup = f"{field}__icontains"
            q_objects |= Q(**{lookup: search_query})
        
        return queryset.filter(q_objects)

    def apply_sorting(self, queryset):
        sort_param = self.request.GET.get("sort", "id_asc")  # Voreingestellte Sortierung nach id_asc
        sort_field = sort_param.replace("_asc", "").replace("_desc", "")  # Entfern von _asc/_desc

        if sort_param.endswith("_desc"):
            sort_field = f"-{sort_field}"

        return queryset.order_by(sort_field)

    def get_paginated_queryset(self, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = self.object
        
        # Фильтрация и сортировка доставок
        deliveries = Delivery.objects.filter(supplier=supplier)
        deliveries = self.apply_search(deliveries)
        deliveries = self.apply_sorting(deliveries)

        context["page_obj"] = self.get_paginated_queryset(deliveries)
        context["search_query"] = self.request.GET.get("search", "")
        context["sort"] = self.request.GET.get("sort", "id")  # Передаем текущий параметр сортировки в шаблон
        return context
