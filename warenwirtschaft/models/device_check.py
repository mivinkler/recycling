from django.db import models
from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.models.material import Material


class DeviceCheck(models.Model):
    SOURCE_CHOICES = [
        (1, "Unload"),
        (2, "Recycling"),
    ]

    STATUS_CHOICES = [
        (1, "Aktiv"),
        (2, "Bereit für Behandlung"),
        (3, "Bereit für Abholung"),
        (4, "Erledigt"),
        (5, "Bereit für Halle 2"),
    ]

    PURPOSE_CHOICES = [
        (1, "Interne Verwendung"),
        (2, "Online-Verkauf"),
        (3, "Barverkauf"),
        (4, "Geschenk"),
        (5, "Austausch"),
    ]

    # Herkunft
    source = models.PositiveSmallIntegerField(choices=SOURCE_CHOICES)

    unload = models.ForeignKey(
        Unload,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="device_checks",
    )

    recycling = models.ForeignKey(
        Recycling,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="device_checks",
    )

    box_type = models.PositiveSmallIntegerField()
    material = models.ForeignKey(Material, on_delete=models.CASCADE, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    purpose = models.PositiveSmallIntegerField(choices=PURPOSE_CHOICES)
    note = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
