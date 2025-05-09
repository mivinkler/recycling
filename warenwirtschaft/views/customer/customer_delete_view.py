from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from warenwirtschaft.models.customer import Customer

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customer/customer_delete.html'
    context_object_name = 'customer'
    success_url = reverse_lazy('customer_list')