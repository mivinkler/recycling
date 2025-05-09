from django.db import models
from warenwirtschaft.models.supplier import Supplier

class Delivery(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='delivery_supplier')
    delivery_receipt = models.CharField(max_length=30, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)