from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from warenwirtschaft.models import Supplier
from warenwirtschaft.forms import SupplierForm


class SupplierUpdateView(UpdateView):
    model = Supplier
    template_name = 'supplier/supplier_update.html'
    form_class = SupplierForm
    context_object_name = 'supplier'

    def get_success_url(self):
        return reverse_lazy('suppliers_list')
