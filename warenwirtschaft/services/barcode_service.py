
import barcode
from io import BytesIO
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile

class BarcodeGenerator:
    """
    Generiert ein Barcode-Bild und speichert es im angegebenen Verzeichnis.
    """
    def __init__(self, obj, code, upload_to):
        self.obj = obj
        self.code = code
        self.upload_to = upload_to

    def generate_image(self):
        ean = barcode.get('code128', self.code, writer=ImageWriter())
        buffer = BytesIO()
        ean.write(buffer)
        file_name = f"{self.upload_to}/{self.code}.png"
        self.obj.barcode_image.save(file_name, ContentFile(buffer.getvalue()), save=False)