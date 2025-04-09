from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from warenwirtschaft.models import Supplier
from warenwirtschaft.forms import SupplierForm

class SupplierUpdateView(UpdateView):
    model = Supplier
    template_name = 'supplier/supplier_update.html'
    form_class = SupplierForm
    context_object_name = 'supplier'
    success_url = reverse_lazy('suppliers_list')
