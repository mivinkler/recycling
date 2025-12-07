from django.db import models
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingWeight(models.Model):
    """
    Historientabelle für Gewicht und Status eines Recycling-Vorgangs.
    Einträge werden automatisch von WeightHistoryMixin erstellt.
    """

    recycling = models.ForeignKey("warenwirtschaft.Recycling", on_delete=models.CASCADE, related_name="weights")
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=StatusChoices.CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return f"{self.weight} kg - {self.get_status_display()}"
