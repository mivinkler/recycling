from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models.supplier import Supplier

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'supplier/supplier_delete.html'
    context_object_name = 'supplier'
    success_url = reverse_lazy('supplier_list')