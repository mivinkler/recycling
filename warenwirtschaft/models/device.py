from django.db import models
from .abstract_model import AbstractModel

class Device(AbstractModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name