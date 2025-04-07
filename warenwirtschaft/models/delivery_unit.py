from django.db import models
from .delivery import Delivery
from .material import Material

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

    # TODO related_name anwenden
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='deliveryunits')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name='material')
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    delivery_type = models.PositiveSmallIntegerField(choices=DELIVERY_TYPE_CHOICES)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.get_delivery_type_display()} - {self.weight} kg"
