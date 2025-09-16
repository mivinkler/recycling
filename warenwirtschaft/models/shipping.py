from django.db import models
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.unload import Unload

class Shipping(models.Model):
    TRANSPORT_CHOICES = [
        (1, "Kunde"),
        (2, "Eigen"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='shipping_for_customer')
    unload = models.ForeignKey(Unload, on_delete=models.CASCADE,  null=True, blank=True, related_name="unload_for_shipping")
    certificate = models.PositiveIntegerField(null=True, blank=True)
    transport = models.PositiveSmallIntegerField(choices=TRANSPORT_CHOICES)
    note = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=64, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

def __str__(self):
        return f"{self.customer} - {self.certificate} - {self.transport} - {self.note}"