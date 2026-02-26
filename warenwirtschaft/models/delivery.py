from django.db import models
from warenwirtschaft.models.customer import Customer

class Delivery(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='deliveries')
    delivery_receipt = models.CharField(max_length=30, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    b2b = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - Lieferschein: {self.delivery_receipt}"
