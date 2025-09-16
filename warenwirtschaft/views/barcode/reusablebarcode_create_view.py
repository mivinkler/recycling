# views/reusable_barcode_create.py
import uuid
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError, transaction

from warenwirtschaft.models.barcode_generator import BarcodeGenerator
from warenwirtschaft.forms.barcode_generator_form import BarcodeGeneratorForm


class ReusableBarcodeCreateView(CreateView):
    model = BarcodeGenerator
    form_class = BarcodeGeneratorForm
    template_name = 'barcode/reusable_barcode_create.html'

    BARCODE_FIELD = "barcode"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'reusable_barcode_create'
        return context

    def _new_code(self) -> str:
        return f"G{uuid.uuid4().hex[:8].upper()}"

    def form_valid(self, form):
        self.object = form.save(commit=False)

        # 5 Mal versuchen
        for _ in range(5):
            code = self._new_code()
            setattr(self.object, self.BARCODE_FIELD, code)
            try:
                with transaction.atomic():
                    self.object.full_clean()
                    self.object.save()
                return HttpResponseRedirect(self.get_success_url())
            except IntegrityError:
                # wiederholen mit neuem Code
                continue

        return self.form_invalid(form)

    def get_success_url(self):
        return reverse('reusable_barcode_detail', kwargs={'pk': self.object.pk})
