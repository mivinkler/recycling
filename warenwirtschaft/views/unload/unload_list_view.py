from django.views.generic import ListView
from django.core.paginator import Paginator
from django.db.models import Q
from warenwirtschaft.models import unload

class UnloadsListView(ListView):
    model = unload
    template_name = "unload/unload_list.html"
    context_object_name = "unloads"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        filter_mapping = {
            "id": "id",
            "supplier": "supplier__name",
            "delivery_unit": "delivery_unit",
            "unload_type": "unload_type",
            "material": "material",
            "weight": "weight",
            "purpose": "purpose",
            "note": "note",
        }

        filters = {
            field: self.request.GET.get(param)
            for param, field in filter_mapping.items()
            if self.request.GET.get(param)
        }
        if filters:
            queryset = queryset.filter(Q(**filters))

        sort_mapping = {
            "id_asc": "id",
            "id_desc": "-id",
            "supplier_asc": "supplier__name",
            "supplier_desc": "-supplier__name",
            "delivery_unit_asc": "delivery_unit",
            "delivery_unit_desc": "-delivery_unit",
            "unload_type_asc": "unload_type",
            "unload_type_desc": "-unload_type",
            "material_asc": "material",
            "material_desc": "-material",
            "weight_asc": "weight",
            "weight_desc": "-weight",
            "purpose_asc": "purpose",
            "purpose_desc": "-purpose",
            "note_asc": "note",
            "note_desc": "-note",
        }

        sort_field = sort_mapping.get(self.request.GET.get("sort", "id_asc"), "id")
        queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        return context
