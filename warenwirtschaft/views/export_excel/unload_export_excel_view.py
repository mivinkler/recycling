from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.views.export_excel.base_export_excel_view import BaseExportExcelView


class UnloadExportExcelView(BaseExportExcelView):

    model = DeliveryUnit
    filename = "wareneingang.xlsx"
    sheet_title = "Wareneingang"
    header = [
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
    ]

    def get_queryset(self):
        """
        QuerySet optimiert mit select_related für verbundene Modelle.
        """
        return DeliveryUnit.objects.select_related(
            "delivery", "delivery__customer", "material"
        ).all()

    def get_row(self, index, item):
        """
        Baut eine Datenzeile für einen DeliveryUnit-Datensatz.
        """
        return [
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
        ]
