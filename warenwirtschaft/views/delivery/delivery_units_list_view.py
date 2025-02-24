from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from warenwirtschaft.models import DeliveryUnit
from django.db.models.functions import Lower

class DeliveryUnitsListView(ListView):
    model = DeliveryUnit
    template_name = "delivery/delivery_units_list.html"
    context_object_name = "delivery_units"
    paginate_by = 20

    active_fields = [
        "id",
        "delivery__supplier__name",
        "delivery__id",
        "delivery__total_weight",
        "delivery_receipt",
        "delivery__delivery_date",
        "delivery_type",
        "device__name",
        "weight",
        "status",
        "note",
    ]

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
        sort_param = self.request.GET.get("sort", "id_asc")
        sort_field = self.sort_mapping.get(sort_param.replace("_asc", "").replace("_desc", ""), "id")

        if sort_param.endswith("_desc"):
            sort_field = f"-{sort_field}"

        return queryset.order_by(sort_field)

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            "delivery", "delivery__supplier", "device"
        )
        return self.apply_sorting(self.apply_search(queryset))

    def get_paginated_queryset(self, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_obj"] = self.get_paginated_queryset(self.get_queryset())
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")
        context["delivery_types"] = DeliveryUnit.DELIVERY_TYPE_CHOICES
        context["statuses"] = DeliveryUnit.STATUS_CHOICES
        return context
