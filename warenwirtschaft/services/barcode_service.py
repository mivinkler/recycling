import uuid
import barcode
from io import BytesIO
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile

def generate_barcode(obj):
    """
    Generiert einen eindeutigen Barcode und speichert ihn als PNG im Verzeichnis,
    Erwartet, dass das Objekt die Felder 'barcode' und 'barcode_image' besitzt.
    """
    code = str(uuid.uuid4()).replace("-", "")[:12]
    obj.barcode = code

    # Code128
    ean = barcode.get('code128', code, writer=ImageWriter())
    buffer = BytesIO()
    ean.write(buffer)

    # Das ImageField speichert automatisch im richtigen Pfad entsprechend 'upload_to'
    obj.barcode_image.save(f'{code}.png', ContentFile(buffer.getvalue()), save=False)
