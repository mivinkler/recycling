from django.views.generic.edit import CreateView
from warenwirtschaft.models import Delivery, Device, Supplier
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class DeliveryCreateView(CreateView):
    model = Delivery
    template_name = "delivery/delivery_create.html"
    form_class = DeliveryForm
    paginate_by = 20

    active_fields= ["supplier__id", 
                    "supplier__avv_number", 
                    "supplier__name", 
                    "supplier__street", 
                    "supplier__postal_code", 
                    "supplier__city", 
                    "supplier__phone", 
                    "supplier__email", 
                    "supplier__note"
                    ]

    def get_queryset(self):
        queryset = super().get_queryset().select_related("supplier")

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
