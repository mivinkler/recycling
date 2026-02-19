from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models_common.choices import BoxTypeChoices


class DeviceCheck(models.Model):
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='device_checks')
    box_type = models.PositiveSmallIntegerField(choices=BoxTypeChoices.CHOICES, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    unload = models.ForeignKey("warenwirtschaft.Unload", on_delete=models.CASCADE, null=True, blank=True, related_name="device_checks")
    recycling = models.ForeignKey("warenwirtschaft.Recycling", on_delete=models.CASCADE, null=True, blank=True, related_name="device_checks")
    created_at = models.DateTimeField(auto_now_add=True)
