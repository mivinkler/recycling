from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import BarcodeGenerator

class BarcodeDeliveryAPI(View):
    def get(self, request):
        # Barcode aus der URL lesen (Parameter heißt "barcode")
        barcode = request.GET.get("barcode", "").strip().upper()
        prefix = barcode[:1]

        if prefix != "G":
            return JsonResponse(
                {'error': 'Nur Barcodes mit G-Präfix sind für Wareneingang gültig.'},
                status=400
            )

        try:
            # Suche nach dem Barcode in der Spalte "barcode"
            generated = BarcodeGenerator.objects.get(barcode__iexact=barcode)

            return JsonResponse({
                'type': 'generated',
                'barcode': generated.barcode,
                'customer': generated.customer_id or None,
                'delivery_receipt': generated.receipt or None,
                'box_type': generated.box_type or None,
                'material': generated.material_id or None,
                'material': generated.material_id or None,
                'weight': generated.weight or None,
            })
        except BarcodeGenerator.DoesNotExist:
            return JsonResponse(
                {'error': 'BarcodeGenerator nicht gefunden'},
                status=404
            )
