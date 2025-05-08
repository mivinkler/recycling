from django.db import models
from warenwirtschaft.models.customer import Customer

class Shipping(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='shipping_for_customer')
    delivery_receipt = models.CharField(max_length=50, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)