from django.db import models
from .supplier import Supplier

class Delivery(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='deliveries')
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    delivery_receipt = models.CharField(max_length=50, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.supplier} • {self.total_weight}kg"