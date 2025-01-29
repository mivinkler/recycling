from django.db import models
from .delivery import Delivery
from .device import Device

class DeliveryUnit(models.Model):
    STATUS_CHOICES = [
        (1, "Eingang"),
        (2, "Zerlegung"),
        (3, "Erledigt"),
    ]

    DELIVERY_TYPE_CHOICES = [
        (1, "Container"),
        (2, "Gitterbox"),
        (3, "Palette"),
        (4, "Ohne Behälter"),
    ]

    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveryunits')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    note = models.CharField(max_length=255, null=True, blank=True)
    delivery_receipt = models.CharField(max_length=50, null=True, blank=True)
    delivery_type = models.PositiveSmallIntegerField(choices=DELIVERY_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.get_delivery_type_display()} - {self.weight} kg - {self.device}"
