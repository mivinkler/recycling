import uuid
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models
from warenwirtschaft.models.supplier import Supplier

class Delivery(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='delivery_supplier')
    delivery_receipt = models.CharField(max_length=30, null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    # 🆕 Barcode-Daten
    barcode = models.CharField(max_length=64, blank=True, null=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def generate_barcode(self):
        """
        Generiert einen eindeutigen Barcode-Wert und speichert das Bild als PNG.
        """
        code = str(uuid.uuid4()).replace("-", "")[:12]
        self.barcode = code

        # Barcode als Bild generieren (Code128-Format)
        ean = barcode.get('code128', code, writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)

        # Im ImageField speichern
        self.barcode_image.save(f'barcode_{code}.png', ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return f"Lieferant: {self.supplier.name} - Lieferschein: {self.delivery_receipt} - Datum: {self.created_at.strftime('%d-%m-%Y %H:%M:%S')}"
