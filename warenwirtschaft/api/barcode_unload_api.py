from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import DeliveryUnit, BarcodeGenerator

class BarcodeUnloadAPI(View):
    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        prefix = code[:1]

        if prefix == "L":
            try:
                unit = DeliveryUnit.objects.get(BARCODE_PREFIX=code)
                return JsonResponse({
                    'type': 'delivery_unit',
                    'delivery_unit_id': unit.id,
                })
            except DeliveryUnit.DoesNotExist:
                return JsonResponse({'error': 'Liefereinheit nicht gefunden'}, status=404)

        return JsonResponse({'error': 'Unbekannter Barcode-Typ'}, status=400)