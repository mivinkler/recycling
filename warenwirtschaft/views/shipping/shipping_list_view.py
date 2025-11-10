from django.views.generic import ListView
from django.db.models import Prefetch, F
from warenwirtschaft.models import Shipping, Unload, Recycling
from warenwirtschaft.services.pagination_service import PaginationService
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService


class ShippingListView(ListView):
    model = Shipping
    template_name = "shipping/shipping_list.html"
    context_object_name = "shippings"
    paginate_by = 28

    def get_queryset(self):
        # Prefetch Unload и Recycling вместе с материалами
        unload_prefetch = Prefetch('unload_for_shipping', queryset=Unload.objects.select_related('material'))
        recycling_prefetch = Prefetch('recycling_for_shipping', queryset=Recycling.objects.select_related('material'))

        queryset = Shipping.objects.select_related('customer') \
            .prefetch_related(unload_prefetch, recycling_prefetch)

        # Поля для поиска/сортировки
        fields = [
            'id', 'customer__name', 'certificate', 'note', 'created_at',
            'transport', 
            'unload_for_shipping__material__name',
            'unload_for_shipping__weight',
            'unload_for_shipping__box_type',
            'unload_for_shipping__status',
            'recycling_for_shipping__material__name',
            'recycling_for_shipping__weight',
            'recycling_for_shipping__box_type',
            'recycling_for_shipping__status',
        ]

        # Выборки для полей с choices
        choices_fields = {
            'transport': dict(Shipping.TRANSPORT_CHOICES),
            'unload_for_shipping__box_type': dict(Unload.BOX_TYPE_CHOICES),
            'recycling_for_shipping__box_type': dict(Recycling.BOX_TYPE_CHOICES),
            'unload_for_shipping__status': dict(Unload.STATUS_CHOICES),
            'recycling_for_shipping__status': dict(Recycling.STATUS_CHOICES),
        }

        search_service = SearchService(self.request, fields, choices_fields)
        sorting_service = SortingService(self.request, fields)

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.object_list)
        context.update({
            'page_obj': page_obj,
        })
        return context
