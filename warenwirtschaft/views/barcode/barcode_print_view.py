from django.apps import apps
from django.http import Http404
from django.views.generic import DetailView

class BarcodePrintView(DetailView):
    template_name = 'barcode/print.html'
    context_object_name = 'obj'

    def get_object(self):
        model_name = self.kwargs.get('model')
        pk = self.kwargs.get('pk')

        # Dynamisches Laden der Modellklasse
        try:
            model = apps.get_model('warenwirtschaft', model_name)
        except LookupError:
            raise Http404("Modell nicht gefunden")

        if not model:
            raise Http404("Modell ungültig")

        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise Http404("Objekt nicht gefunden")
