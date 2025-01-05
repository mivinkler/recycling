from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from warenwirtschaft.models import Supplier
from warenwirtschaft.forms import SupplierForm


class SupplierCreateView(CreateView):
    model = Supplier
    template_name = "supplier/supplier_create.html"
    form_class = SupplierForm

    def get_success_url(self):
        return reverse_lazy("supplier_detail", kwargs={"pk": self.object.pk})
