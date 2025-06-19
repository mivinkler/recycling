from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.supplier import Supplier

class ReusableBarcode(models.Model):
    STEP_CHOICES = [
        (1, 'Lieferung'),
        (2, 'Umladung'),
        (3, 'Recycling'),
        (4, 'Versand'),
    ]

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
    step = models.PositiveSmallIntegerField(choices=STEP_CHOICES, blank=True, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name='supplier_for_barcode')
    box_type = models.PositiveSmallIntegerField(choices=BOX_TYPE_CHOICES, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='material_for_barcode')
    target = models.PositiveSmallIntegerField(choices=TARGET_CHOICES, blank=True, null=True)
    barcode_image = models.ImageField(upload_to='barcodes/reusable', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.code} ({self.get_box_type_display()})"
