from django.http import HttpResponse
from openpyxl import Workbook
from warenwirtschaft.models import Unload


class UnloadExportExcel:
    """
    Klasse für den Excel-Export der Wareneingang-Daten.
    Enthält Logik zum Erstellen der Excel-Datei und Rückgabe
    einer HttpResponse.
    """

    @staticmethod
    def build_workbook(qs):
        """
        Erstellt eine Excel-Arbeitsmappe basierend auf dem QuerySet.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Wareneingang"

        # Kopfzeile
        ws.append([
            "№",
            "LID",
            "EID",
            "Datum",
            "Kunde",
            "Lieferschein",
            "Behälter",
            "Material",
            "Gewicht (kg)",
            "Status",
            "Anmerkung",
        ])

        # Datenzeilen
        for index, item in enumerate(qs, start=1):
            ws.append([
                index,
                item.delivery_id,
                item.id,
                item.created_at.strftime("%d.%m.%Y") if item.created_at else "",
                item.delivery.customer.name if item.delivery and item.delivery.customer else "",
                item.delivery.delivery_receipt if item.delivery else "",
                item.get_box_type_display(),
                item.material.name if item.material else "-",
                item.weight,
                item.get_status_display(),
                item.note or "",
            ])

        return wb

    @staticmethod
    def export_response(qs):
        """
        Gibt die Excel-Datei als HttpResponse zurück.
        """
        wb = UnloadExcelExporter.build_workbook(qs)

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="wareneingang.xlsx"'

        wb.save(response)
        return response


# --- View-Funktion (sehr klein, da Logik im Exporter steckt) ---

def unload_export_excel(request):
    # QuerySet vorbereiten
    qs = Unload.objects.select_related(
        "unload", "material"
    ).all()

    return UnloadExcelExporter.export_response(qs)
