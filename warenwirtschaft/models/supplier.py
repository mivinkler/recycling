from django.db import models
from .abstract_model import AbstractModel

class Supplier(AbstractModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    avv_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="AVV-Nummer")
    street = models.CharField(max_length=100, null=True, blank=True, verbose_name="Straße")
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="PLZ")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Stadt")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefon")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    note = models.CharField(max_length=255, null=True, blank=True, verbose_name="Bemerkung")

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["avv_number"]),
        ]

    def __str__(self):
        avv_number = self.avv_number if self.avv_number else "Unknown AVV number"
        return f"{self.name} (AVV: {avv_number})"