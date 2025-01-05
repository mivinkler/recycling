from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from warenwirtschaft.models import Supplier, Delivery


class SupplierDetailView(DetailView):
    model = Supplier
    template_name = 'supplier/supplier_detail.html'
    context_object_name = 'supplier'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        supplier = self.object

        deliveries = Delivery.objects.filter(supplier=supplier)

        paginator = Paginator(deliveries, 14)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context
