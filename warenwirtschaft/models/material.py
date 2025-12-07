from django.db import models


class Material(models.Model):
    name = models.CharField(max_length=50, unique=True)
    delivery = models.BooleanField(default=False)
    unload = models.BooleanField(default=False)
    recycling = models.BooleanField(default=False)
    device_check = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["delivery"]),
            models.Index(fields=["unload"]),
            models.Index(fields=["recycling"]),
            models.Index(fields=["device_check"]),
        ]

    def __str__(self):
        return self.name