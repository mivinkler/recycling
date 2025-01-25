from django.db import models
from .abstract_model import AbstractModel
from .supplier import Supplier

class Delivery(AbstractModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    units = models.IntegerField(null=True, blank=True)
    delivery_receipt = models.CharField(max_length=50, null=True, blank=True)
    delivery_date = models.DateField()
    note = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.supplier} • {self.weight}kg"