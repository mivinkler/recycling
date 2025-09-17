from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.customer import Customer


class BarcodeGenerator(models.Model):
    BOX_TYPE_CHOICES = [
        (1, "Container"),              
        (2, "Gitterbox"),
        (3, "Palette"),
        (4, "Gelbe Waagen"),
        (5, "Ohne Behälter"),
    ]

    TRANSPORT_CHOICES = [
        (1, "Kunde"),
        (2, "Eigen"),
    ]


    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, related_name='customer_for_barcode')
    receipt = models.CharField(max_length=100, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='material_for_barcode')
    box_type = models.PositiveSmallIntegerField(choices=BOX_TYPE_CHOICES, blank=True, null=True)
    transport = models.PositiveSmallIntegerField(choices=TRANSPORT_CHOICES, default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    barcode = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.code} ({self.get_box_type_display()})"
