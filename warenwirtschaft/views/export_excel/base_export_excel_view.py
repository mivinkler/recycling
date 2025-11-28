from django.http import HttpResponse
from django.views import View
from openpyxl import Workbook


class BaseExportExcelView(View):
    # Basis-Einstellungen, können in Subklassen überschrieben werden
    model = None                # Modellklasse
    filename = "export.xlsx"    # Dateiname für den Download
    sheet_title = "Daten"       # Titel des Arbeitsblatts
    header = []                 # Kopfzeile (Liste von Spaltennamen)

    def get_queryset(self):
        """
        Standard-QuerySet. In Subklassen überschreiben,
        wenn select_related()/filter() benötigt wird.
        """
        if self.model is None:
            raise ValueError("model muss in der Subklasse definiert werden.")
        return self.model.objects.all()

    def get_row(self, index, obj):
        """
        Muss in der Subklasse implementiert werden.
        Baut eine Datenzeile für das Excel-Sheet.
        """
        raise NotImplementedError("get_row() muss in der Subklasse implementiert werden.")

    def get(self, request, *args, **kwargs):
        # QuerySet holen
        qs = self.get_queryset()

        # Neues Excel-Workbook erstellen
        wb = Workbook()
        ws = wb.active
        ws.title = self.sheet_title

        # Kopfzeile schreiben (falls definiert)
        if self.header:
            ws.append(self.header)

        # Datenzeilen schreiben
        for index, obj in enumerate(qs, start=1):
            ws.append(self.get_row(index, obj))

        # HTTP-Antwort mit Excel-Datei
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="{self.filename}"'

        wb.save(response)
        return response
