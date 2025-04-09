from django.views.generic.edit import DeleteView
from warenwirtschaft.models import Supplier
from django.urls import reverse_lazy

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'supplier/supplier_delete.html'
    context_object_name = 'supplier'
    success_url = reverse_lazy('suppliers_list')