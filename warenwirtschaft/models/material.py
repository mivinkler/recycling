from django.db import models


class Material(models.Model):
    name = models.CharField(max_length=50, unique=True)
    delivery = models.BooleanField(default=False)
    unload = models.BooleanField(default=False)
    recycling = models.BooleanField(default=False)
    halle_zwei = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["delivery"]),
            models.Index(fields=["unload"]),
            models.Index(fields=["recycling"]),
            models.Index(fields=["halle_zwei"]),
        ]

    def __str__(self):
        return self.name