from django.db import models

class Device(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Name")
    avv_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="AVV-Nummer")
    street = models.CharField(max_length=100, null=True, blank=True, verbose_name="Straße")
    postal_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="PLZ")
    city = models.CharField(max_length=50, null=True, blank=True, verbose_name="Stadt")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Telefon")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    note = models.CharField(max_length=255, null=True, blank=True, verbose_name="Bemerkung")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["avv_number"]),
        ]

    def __str__(self):
        avv_number = self.avv_number if self.avv_number else "Unknown AVV number"
        return f"{self.name} (AVV: {avv_number})"

class Delivery(models.Model):
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    units = models.IntegerField(null=True, blank=True)
    delivery_receipt = models.CharField(max_length=50, null=True, blank=True)
    delivery_date = models.DateField()
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.supplier} • {self.weight}kg"
    

class DeliveryUnits(models.Model):
    STATUS_CHOICES = [
        (1, "Eingang"),
        (2, "Zerlegung"),
        (3, "Erledigt"),
    ]

    DELIVERY_TYPE_CHOICES = [
        (1, "Container"),
        (2, "Gitterbox"),
        (3, "Palette"),
        (4, "Ohne Behälter"),
    ]

    delivery = models.ForeignKey("Delivery", on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveryunits')
    device = models.ForeignKey("Device", on_delete=models.CASCADE, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    note = models.CharField(max_length=255, null=True, blank=True)
    delivery_receipt = models.CharField(max_length=50, null=True, blank=True)
    delivery_type = models.PositiveSmallIntegerField(choices=DELIVERY_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.device} ({self.delivery.delivery_date})"

