from django.db import models
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.material import Material

class DeliveryUnit(models.Model):
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

    TARGET_CHOICES = [
        (1, "Umladung"),
        (2, "Recycling"),
        (3, "Abholung"),
        (4, "Entsorgung"),
    ]

    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='units_for_delivery')
    box_type = models.PositiveSmallIntegerField(choices=BOX_TYPE_CHOICES)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name='material_for_delivery_units')
    material_other = models.CharField(max_length=50, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    target = models.PositiveSmallIntegerField(choices=TARGET_CHOICES)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    note = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=64, blank=True, null=True)
    barcode_image = models.ImageField(upload_to='barcodes/delivery/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"ID: {self.id} - {self.get_box_type_display()} - {self.material} - {self.weight} kg - {self.status}"
