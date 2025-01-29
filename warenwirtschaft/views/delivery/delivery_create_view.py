from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from warenwirtschaft.models import Delivery
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.models import Device
from warenwirtschaft.models import Supplier
from django.core.paginator import Paginator
from django.db.models import Q


class DeliveryCreateView(CreateView):
    model = Delivery
    template_name = "delivery/delivery_create.html"
    form_class = DeliveryForm
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        filter_mapping = {
            'id': 'id',
            'avv_number': 'avv_number',
            'name': 'name',
            'street': 'street',
            'postal_code': 'postal_code',
            'city': 'city',
        }

        filters = {
            field: self.request.GET.get(param)
            for param, field in filter_mapping.items()
            if self.request.GET.get(param)
        }

        if filters:
            queryset = queryset.filter(Q(**filters))

        sort_mapping = {
            'id_asc': 'id', 
            'id_desc': '-id',
            'avv_number_asc': 'avv_number', 
            'avv_number_desc': '-avv_number',
            'name_asc': 'name', 
            'name_desc': '-name',
            'street_asc': 'street', 
            'street_desc': '-street',
            'postal_code_asc': 'postal_code', 
            'postal_code_desc': '-postal_code',
            'city_asc': 'city', 
            'city_desc': '-city',
        }

        sort_field = sort_mapping.get(self.request.GET.get('sort', 'id_asc'), 'id')
        queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['devices'] = Device.objects.all()

        suppliers_list = Supplier.objects.all()
        supplier_paginator = Paginator(suppliers_list, self.paginate_by)
        supplier_page_number = self.request.GET.get('supplier_page', 1)
        supplier_page_obj = supplier_paginator.get_page(supplier_page_number)

        context['page_obj'] = supplier_page_obj
        return context
