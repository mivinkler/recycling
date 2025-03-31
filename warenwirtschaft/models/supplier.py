from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    avv_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="AVV-Nummer")
    street = models.CharField(max_length=100, null=True, blank=True, verbose_name="Straße")
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="PLZ")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Stadt")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefon")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    note = models.CharField(max_length=255, null=True, blank=True, verbose_name="Anmerkung")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["avv_number"]),
        ]

    def __str__(self):
        return f"{self.name}\n{self.street}\n{self.postal_code} {self.city}\nAVV: {self.avv_number}"