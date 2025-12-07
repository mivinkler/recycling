# warenwirtschaft/models/deactivate_time_mixin.py
from django.db import models
from django.utils import timezone


class DeactivateTimeMixin(models.Model):
    """
    Abstraktes Mixin, das die Aktiv/Inaktiv-Logik für Modelle bereitstellt.
    """

    is_active = models.BooleanField(default=True)
    inactive_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        # Wenn Objekt deaktiviert wird -> Zeit setzen
        if not self.is_active and self.inactive_at is None:
            self.inactive_at = timezone.now()

        # Wenn Objekt reaktiviert wird -> Zeit löschen
        if self.is_active and self.inactive_at is not None:
            self.inactive_at = None

        return super().save(*args, **kwargs)
