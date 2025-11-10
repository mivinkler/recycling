from django.db import models
from warenwirtschaft.models.material import Material

class Recycling(models.Model):
    BOX_TYPE_CHOICES = [
        (1, "Gitterbox"),
        (2, "Palette"),
        (3, "Gelbe Waagen"),
        (4, "Ohne Behälter"),
    ]

    STATUS_CHOICES = [
        (1, "Aktiv"),
        (3, "Bereit für Abholung"),
        (4, "Erledigt"),
    ]

    unloads = models.ManyToManyField("warenwirtschaft.Unload", related_name="recycling_for_unload")
    box_type = models.PositiveSmallIntegerField(choices=BOX_TYPE_CHOICES)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name="material_for_recycling")
    material_other = models.CharField(max_length=50, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    note = models.CharField(max_length=255, null=True, blank=True)
    shipping = models.ForeignKey('warenwirtschaft.Shipping', on_delete=models.SET_NULL, null=True, blank=True, related_name='recycling_for_shipping')
    barcode = models.CharField(max_length=64, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"ID: {self.id} - {self.get_box_type_display()} - {self.weight} kg - {self.status}"
