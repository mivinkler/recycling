from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from warenwirtschaft.forms import SupplierForm
from warenwirtschaft.models.supplier import Supplier

class SupplierUpdateView(UpdateView):
    model = Supplier
    template_name = 'supplier/supplier_update.html'
    form_class = SupplierForm
    context_object_name = 'supplier'
    success_url = reverse_lazy('supplier_list')
