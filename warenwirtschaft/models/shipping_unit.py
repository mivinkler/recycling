from django.db import models
from warenwirtschaft.models.shipping import Shipping
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.recycling import Recycling

class ShippingUnit(models.Model):
    STATUS_CHOICES = [
        (1, "Aktiv"),
        (2, "Erledigt"),
    ]

    BOX_TYPE_CHOICES = [
        (1, "Container"),
        (2, "Gitterbox"),
        (3, "Palette"),
        (4, "Ohne Behälter"),
    ]

    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name='shipping_units_for_shipping')
    recycling = models.ForeignKey(Recycling, on_delete=models.CASCADE,  null=True, blank=True, related_name="shipping_units_for_recycling")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name='material_for_shipping_units')
    material_other = models.CharField(max_length=50, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    box_type = models.PositiveSmallIntegerField(choices=BOX_TYPE_CHOICES)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"ID: {self.id} - {self.get_box_type_display()} - {self.material} - {self.weight} kg"
