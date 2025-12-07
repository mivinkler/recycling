from django.db import models
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models_common.choices import TransportChoices
from warenwirtschaft.models_common.mixins import DeactivateTimeMixin


class Shipping(DeactivateTimeMixin, models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='shippings')
    certificate = models.PositiveIntegerField(null=True, blank=True)
    transport = models.PositiveSmallIntegerField(choices=TransportChoices.CHOICES)
    note = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} - {self.certificate} - {self.get_transport_display()}"
