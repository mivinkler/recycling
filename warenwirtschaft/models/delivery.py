from django.db import models
from warenwirtschaft.models.customer import Customer

class Delivery(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='delivery_customer')
    delivery_receipt = models.CharField(max_length=30, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"Lieferant: {self.customer.name} - Lieferschein: {self.delivery_receipt}"
