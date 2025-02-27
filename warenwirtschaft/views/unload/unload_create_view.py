from django.views.generic.edit import CreateView
from warenwirtschaft.forms import UnloadForm
from warenwirtschaft.models import Device, Unload, DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class UnloadCreateView(CreateView):
    model = Unload
    template_name = "unload/unload_create.html"
    form_class = UnloadForm
    paginate_by = 20

    active_fields = ["deliveryunits__delivery_unit", 
                    "deliveryunits__unload_type", 
                    "deliveryunits__device", 
                    "deliveryunits__weight", 
                    "deliveryunits__purpose", 
                    "deliveryunits__note", 
                    "deliveryunits__supplier",
                    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("delivery_unit")

        search_service = SearchService(self.request, self.active_fields)
        sorting_service = SortingService(self.request, self.active_fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["devices"] = Device.objects.all()
        context["search_query"] = self.request.GET.get("search", "")
        context["sort_param"] = self.request.GET.get("sort", "")

        return context