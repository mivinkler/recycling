from django.db import models
from warenwirtschaft.models_common.choices import StatusChoices


class HalleZwei(models.Model):
    delivery_unit = models.OneToOneField("warenwirtschaft.DeliveryUnit", on_delete=models.PROTECT, related_name="delivery_to_halle_zwei")
    status = models.PositiveSmallIntegerField(choices=StatusChoices.CHOICES, default=StatusChoices.AKTIV_IN_HALLE_ZWEI)
    note = models.CharField(max_length=255, null=True, blank=True)

    halle_zwei = models.BooleanField(null=True, blank=True)
    shipping = models.ForeignKey("warenwirtschaft.Shipping", on_delete=models.PROTECT, null=True, blank=True, related_name="halle_zweis")

    created_at = models.DateTimeField(auto_now_add=True)
    inactive_at = models.DateTimeField(null=True, blank=True)
    