from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator
from warenwirtschaft.models import Supplier


class SupplierListView(ListView):
    model = Supplier
    template_name = 'supplier/supplier_list.html'
    context_object_name = 'suppliers'
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
            'phone': 'phone',
            'email': 'email',
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
            'phone_asc': 'phone', 
            'phone_desc': '-phone',
            'email_asc': 'email', 
            'email_desc': '-email',
            'note_asc': 'note', 
            'note_desc': '-note',
        }

        sort_field = sort_mapping.get(self.request.GET.get('sort', 'id_asc'), 'id')
        queryset = queryset.order_by(sort_field)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context
