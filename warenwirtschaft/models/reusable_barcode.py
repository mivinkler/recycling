from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.unload import Unload


class ReusableBarcode(models.Model):
    BOX_TYPE_CHOICES = [
        (1, "Gitterbox"),
        (2, "Palette"),
        (3, "Gelbe Waagen"),
        (4, "Ohne Behälter"),
    ]

    TARGET_CHOICES = [
        (1, "Umladung"),
        (2, "Recycling"),
        (3, "Abholung"),
        (4, "Entsorgung"),
    ]
        
    code = models.CharField(max_length=64, unique=True)
    box_type = models.PositiveSmallIntegerField(choices=Unload.BOX_TYPE_CHOICES)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True, related_name='material_for_barcode')
    target = models.PositiveSmallIntegerField(choices=TARGET_CHOICES)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)


    def __str__(self):
        return f"{self.code} ({self.get_box_type_display()})"