from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from warenwirtschaft.models import Delivery, DeliveryUnit

class DeliveryListView(ListView):
    model = Delivery
    template_name = "delivery/delivery_list.html"
    context_object_name = "deliveries"
    paginate_by = 20

    search_fields = [
        "id", "supplier__name", "units", "delivery_receipt", "weight", "delivery_date", "note",
        "deliveryunit__id", "deliveryunit__delivery_receipt", "deliveryunit__delivery_type",
        "deliveryunit__device__name", "deliveryunit__weight", "deliveryunit__status", "deliveryunit__note"
    ]

    sort_mapping = {field: field for field in search_fields if "__" not in field}
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
        sort_field = self.sort_mapping.get(self.request.GET.get("sort"), "id")
        return queryset.order_by(sort_field)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
            Prefetch("deliveryunit_set", queryset=DeliveryUnit.objects.all())
        )
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
        context["sort_param"] = self.request.GET.get("sort", "")
        context["delivery_types"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES
        return context
