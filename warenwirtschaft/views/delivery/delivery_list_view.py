from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from warenwirtschaft.models import Delivery, DeliveryUnit
from django.db.models import OuterRef, Subquery

class DeliveryListView(ListView):
    model = Delivery
    template_name = "delivery/delivery_list.html"
    context_object_name = "deliveries"
    paginate_by = 20

    search_fields = ["id", 
                     "supplier__name", 
                     "units", 
                     "delivery_receipt", 
                     "weight", 
                     "created_at", 
                     "note", 
                     "delivery_units__id", 
                     "delivery_units__delivery_receipt",
                     "delivery_units__delivery_type", 
                     "delivery_units__material__name",
                     "delivery_units__weight", 
                     "delivery_units__status", 
                     "delivery_units__note"]
    
    sort_mapping = {field: field for field in search_fields}
    sort_mapping.update({f"{key}_desc": f"-{val}" for key, val in sort_mapping.items()})

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            first_unit_weight=Subquery(
                DeliveryUnit.objects.filter(delivery=OuterRef("id"))
                .order_by("id")  # Можно менять на другое поле
                .values("weight")[:1]
            )
        ).prefetch_related("deliveryunits")  # Prefetch для отображения связанных данных

        return self.apply_sorting(self.apply_search(queryset))

    def apply_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            q_objects = Q(*[Q(**{f"{field}__icontains": search_query}) for field in self.search_fields], _connector=Q.OR)
            queryset = queryset.filter(q_objects)
        return queryset

    def apply_sorting(self, queryset):
        sort_field = self.sort_mapping.get(self.request.GET.get("sort"), "id")
        return queryset.order_by(sort_field)

    def get_paginated_queryset(self, queryset):
        return Paginator(queryset, self.paginate_by).get_page(self.request.GET.get("page", 1))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "page_obj": self.get_paginated_queryset(self.get_queryset()),
            "search_query": self.request.GET.get("search", ""),
            "sort": self.request.GET.get("sort", "id")
        })
        return context