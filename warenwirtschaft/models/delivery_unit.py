from django.db import models
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.material import Material
from warenwirtschaft.models_common.choices import BoxTypeChoices
from warenwirtschaft.models_common.choices.status_choices import StatusChoices
from warenwirtschaft.models_common.mixins import DeactivateTimeMixin


class DeliveryUnit(DeactivateTimeMixin, models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='delivery_units')
    box_type = models.PositiveSmallIntegerField(choices=BoxTypeChoices.CHOICES, blank=True, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_units')
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=StatusChoices.CHOICES, default=StatusChoices.WARTET_AUF_VORSORTIERUNG)
    note = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=64, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ID: {self.id} - {self.get_box_type_display()} - {self.material} - {self.weight} kg"
    