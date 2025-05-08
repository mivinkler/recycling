from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.delivery_unit import DeliveryUnit


class Unload(models.Model):
    UNLOAD_TYPE_CHOICES = [
        (1, "Gitterbox"),
        (2, "Palette"),
        (3, "Container"),
        (4, "Ohne Behälter"),
    ]

    PURPOSE_CHOICES = [
        (1, "Behandlung"),
        (2, "Abholung"),
        (3, "Entsorgung"),
    ]

    STATUS_CHOICES = [
        (1, "Aktiv"),
        (2, "Erledigt"),
    ]

    delivery_unit = models.ForeignKey(DeliveryUnit, on_delete=models.CASCADE, related_name="unload_for_delivery_unit")
    unload_type = models.PositiveSmallIntegerField(choices=UNLOAD_TYPE_CHOICES)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name="material_for_delivery_unit")
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purpose = models.PositiveSmallIntegerField(choices=PURPOSE_CHOICES)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"unload: {self.delivery_unit} - {self.weight} kg - Type: {self.get_unload_type_display()} - Purpose: {self.get_purpose_display()}"