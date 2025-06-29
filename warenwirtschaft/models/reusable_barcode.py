from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.supplier import Supplier
from warenwirtschaft.models.customer import Customer

class ReusableBarcode(models.Model):
    BOX_TYPE_CHOICES = [
        (1, "Container"),              
        (2, "Gitterbox"),
        (3, "Palette"),
        (4, "Gelbe Waagen"),
        (5, "Ohne Behälter"),
    ]

    AREA_CHOICES = [
        (1, "Eingang"),
        (2, "Umladung"),
        (3, "Aufbereitung"),
        (4, "Abholung"),
        (5, "Entsorgung"),
        (6, "Zusatzdaten"),
    ]
    
    TARGET_CHOICES = [
        (1, "Eingang"),
        (2, "Umladung"),
        (3, "Aufbereitung"),
        (4, "Abholung"),
        (5, "Entsorgung"),
    ]


    code = models.CharField(max_length=64, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, blank=True, null=True, related_name='supplier_for_barcode')
    delivery_receipt = models.CharField(max_length=100, blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, related_name='customer_for_barcode')
    box_type = models.PositiveSmallIntegerField(choices=BOX_TYPE_CHOICES, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='material_for_barcode')
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    area = models.PositiveSmallIntegerField(choices=AREA_CHOICES, blank=True, null=True)
    target = models.PositiveSmallIntegerField(choices=TARGET_CHOICES, blank=True, null=True)
    barcode_image = models.ImageField(upload_to='barcodes/reusable', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.code} ({self.get_box_type_display()})"
