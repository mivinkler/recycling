from django.db import models


class WeightHistoryMixin(models.Model):
    """
    Abstraktes Mixin, das automatisch Historieneinträge für Gewicht und Status erzeugt.

    Erwartungen:
    - Das Modell besitzt die Felder 'weight' und 'status'.
    - Es existiert eine zugehörige History-Tabelle mit einem ForeignKey
      auf dieses Modell und einem Related Name (Standard: 'weights').
    """

    history_related_name = "weights"

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Überschreibt die Speichermethode, um bei Erstellung oder Änderung
        von Gewicht/Status automatisch einen Historieneintrag anzulegen.
        """
        is_create = self.pk is None
        old_weight = None
        old_status = None

        # Alten Zustand nur laden, wenn das Objekt bereits existiert
        if not is_create:
            try:
                old = self.__class__.objects.only("weight", "status").get(pk=self.pk)
                old_weight = old.weight
                old_status = old.status
            except self.__class__.DoesNotExist:
                is_create = True  # Sicherheitsfallback, sollte selten vorkommen

        # Zuerst das eigentliche Objekt speichern (inkl. anderer Mixins)
        super().save(*args, **kwargs)

        # Nur Historie schreiben, wenn:
        # - neues Objekt oder
        # - Gewicht oder Status sich geändert haben
        if is_create or self.weight != old_weight or self.status != old_status:
            history_manager = getattr(self, self.history_related_name)
            history_manager.create(weight=self.weight, status=self.status)
