from django.db import models
from warenwirtschaft.models.material import Material
from warenwirtschaft.models_common.choices import BoxTypeChoices, StatusChoices
from warenwirtschaft.models_common.mixins import WeightHistoryMixin


class Recycling(models.Model):
    unloads = models.ManyToManyField("warenwirtschaft.Unload", related_name="recyclings")
    box_type = models.PositiveSmallIntegerField(choices=BoxTypeChoices.CHOICES, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name="recyclings")
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=StatusChoices.CHOICES, default=StatusChoices.AKTIV_IN_ZERLEGUNG)
    note = models.CharField(max_length=255, null=True, blank=True)
    shipping = models.ForeignKey('warenwirtschaft.Shipping', on_delete=models.SET_NULL, null=True, blank=True, related_name='recyclings')
    barcode = models.CharField(max_length=64, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    inactive_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"ZID: {self.id} - {self.get_box_type_display()} - {self.material} - {self.weight} kg"
    