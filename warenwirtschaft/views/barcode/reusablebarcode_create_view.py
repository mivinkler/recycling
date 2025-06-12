import barcode
from io import BytesIO
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
from barcode.writer import ImageWriter

from warenwirtschaft.models import ReusableBarcode
from warenwirtschaft.forms import ReusableBarcodeForm

import uuid

class ReusableBarcodeCreateView(CreateView):
    model = ReusableBarcode
    form_class = ReusableBarcodeForm
    template_name = 'barcode/reusable_barcode_create.html'
    success_url = reverse_lazy('reusable_barcode_create')

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # Wenn kein Code eingegeben wurde – generieren wir ihn automatisch
        if not self.object.code:
            self.object.code = f"{uuid.uuid4().hex[:8].upper()}"

        # Barcode-Bild generieren
        if self.object.code:
            ean = barcode.get('code128', self.object.code, writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            file_name = f"{self.object.code}.png"
            self.object.barcode_image.save(file_name, ContentFile(buffer.getvalue()), save=False)

        self.object.save()
        return super().form_valid(form)
