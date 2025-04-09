from django.views.generic.edit import CreateView
from warenwirtschaft.models import Supplier
from warenwirtschaft.forms import SupplierForm
from django.urls import reverse_lazy

class SupplierCreateView(CreateView):
    model = Supplier
    template_name = 'supplier/supplier_create.html'
    form_class = SupplierForm
    success_url = reverse_lazy('suppliers_list')
