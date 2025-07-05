from django.db import models

class Material(models.Model):
    name = models.CharField(max_length=50)
    delivery = models.BooleanField(default=False, verbose_name="material_delivery")
    unload = models.BooleanField(default=False, verbose_name="material_unload")
    recycling = models.BooleanField(default=False, verbose_name="material_recycling")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name