from django.db import models
from .delivery_unit import DeliveryUnit
from .supplier import Supplier
from .material import Material

class Unload(models.Model):
    UNLOAD_TYPE_CHOICES = [
        (1, "Gitterbox"),
        (2, "Palette"),
        (3, "Ohne Behälter"),
    ]

    PURPOSE_CHOICES = [
        (1, "Zerlegung"),
        (2, "Reparatur"),
        (3, "Entsorgung"),
    ]

    delivery_unit = models.ForeignKey(DeliveryUnit, on_delete=models.CASCADE, related_name="unload_delivery_unit")
    unload_type = models.PositiveSmallIntegerField(choices=UNLOAD_TYPE_CHOICES)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name="unload_material")
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purpose = models.PositiveSmallIntegerField(choices=PURPOSE_CHOICES)
    note = models.CharField(max_length=255, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="unload_supplier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"unload: {self.delivery_unit} - {self.weight} kg - Type: {self.get_unload_type_display()} - Purpose: {self.get_purpose_display()}"
