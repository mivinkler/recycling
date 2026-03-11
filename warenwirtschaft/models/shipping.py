from django.db import models
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models_common.choices import TransportChoices


class Shipping(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='shippings')
    certificate = models.PositiveIntegerField(null=True, blank=True)
    transport = models.PositiveSmallIntegerField(choices=TransportChoices.CHOICES)
    note = models.CharField(max_length=255, null=True, blank=True)
    barcode = models.CharField(max_length=64, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} - {self.certificate} - {self.get_transport_display()}"

    @property
    def einheiten(self):
        einheiten = []

        for unload in self.unloads.all():
            einheiten.append({
                "typ": "Unload",
                "obj": unload,
                "sortierung": 1,
                "pk": unload.pk,
            })

        for recycling in self.recyclings.all():
            einheiten.append({
                "typ": "Recycling",
                "obj": recycling,
                "sortierung": 2,
                "pk": recycling.pk,
            })

        for halle_zwei in self.halle_zwei.all():
            einheiten.append({
                "typ": "Halle 2",
                "obj": halle_zwei,
                "sortierung": 3,
                "pk": halle_zwei.pk,
            })

        return sorted(einheiten, key=lambda item: (item["sortierung"], item["pk"]))