from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models.barcode_generator import BarcodeGenerator  # genauer Pfad benutzen

class BarcodeDeliveryAPI(View):
    def get(self, request):
        # Barcode aus der URL lesen und normalisieren
        barcode = (request.GET.get("barcode") or "").strip().upper()
        if not barcode:
            return JsonResponse({'error': 'Kein Barcode übergeben.'}, status=400)

        # Präfix prüfen – muss zum Frontend (data-accepted) passen
        if not barcode.startswith("G"):
            return JsonResponse(
                {'error': 'Nur Barcodes mit G-Präfix.'},
                status=400
            )

        try:
            # select_related für schlankeren Zugriff auf FK-Objekte
            generated = (BarcodeGenerator.objects
                         .select_related('customer', 'material')
                         .get(barcode__iexact=barcode))
        except BarcodeGenerator.DoesNotExist:
            return JsonResponse({'error': 'BarcodeGenerator nicht gefunden'}, status=404)

        # Lesbaren Namen ermitteln: bevorzugt Feld 'name', sonst __str__
        customer_name = None
        if generated.customer_id:
            customer_name = getattr(generated.customer, 'name', str(generated.customer))

        # Nur primitive Datentypen zurückgeben (IDs, Strings, Zahlen)
        data = {
            'type': 'generated',
            'barcode': generated.barcode,
            'customer_id': generated.customer_id or None,
            'customer_name': customer_name,
            'delivery_receipt': generated.receipt or None,
            'box_type': generated.box_type or None,          # Choice (int)
            'material': generated.material_id or None,       # nur ID
            'weight': (str(generated.weight)
                       if generated.weight is not None else None),  # Decimal sicher serialisieren
        }
        return JsonResponse(data)
