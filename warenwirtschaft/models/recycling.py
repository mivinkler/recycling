from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.unload import Unload


class Recycling(models.Model):
    BOX_TYPE_CHOICES = [
        (1, "Gitterbox"),
        (2, "Palette"),
        (3, "Gelbe Waagen"),
        (4, "Ohne Behälter"),
    ]

    TARGET_CHOICES = [
        (3, "Abholung"),
        (4, "Entsorgung"),
    ]

    STATUS_CHOICES = [
        (1, "Aktiv"),
        (2, "Erledigt"),
    ]

    unload = models.ForeignKey(Unload, on_delete=models.CASCADE, related_name="recycling_for_unload")
    box_type = models.PositiveSmallIntegerField(choices=BOX_TYPE_CHOICES)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name="material_for_recycling")
    material_other = models.CharField(max_length=50, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target = models.PositiveSmallIntegerField(choices=TARGET_CHOICES)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.get_box_type_display()} - {self.material_other} - {self.weight} kg - {self.target} - {self.status}"