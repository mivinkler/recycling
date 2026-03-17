from django.views.generic.detail import DetailView

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.pagination_service import PaginationPreferenceMixin, PaginationService


class CustomerDetailView(PaginationPreferenceMixin, DetailView):
    model = Customer
    template_name = "customer/customer_detail.html"
    context_object_name = "customer"
    paginate_by = 14

    def get_queryset(self):
        return super().get_queryset()

    def get_deliveryunits_queryset(self):
        customer = self.get_object()

        return (
            DeliveryUnit.objects
            .select_related("delivery", "delivery__customer", "material")
            .filter(delivery__customer=customer)
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        deliveryunits = self.get_deliveryunits_queryset()
        current_page_size = self.get_current_page_size(self.paginate_by)
        page_obj = PaginationService(
            self.request,
            current_page_size,
            page_size_param=self.page_size_param,
            cookie_name=self.page_size_cookie_name,
            min_page_size=self.min_page_size,
            max_page_size=self.max_page_size,
        ).get_paginated_queryset(deliveryunits)

        context.update(
            {
                "page_obj": page_obj,
                "deliveryunits": page_obj,
                "selected_menu": "customer_list",
            }
        )
        context.update(self.get_page_size_context(page_obj.paginator.per_page))
        return context
