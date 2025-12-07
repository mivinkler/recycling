from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models_common.choices import BoxTypeChoices, TransportChoices


class BarcodeGenerator(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True, related_name='barcodes')
    receipt = models.CharField(max_length=100, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='barcodes')
    box_type = models.PositiveSmallIntegerField(choices=BoxTypeChoices.CHOICES, blank=True, null=True)
    transport = models.PositiveSmallIntegerField(choices=TransportChoices.CHOICES, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    barcode = models.CharField(max_length=64, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
