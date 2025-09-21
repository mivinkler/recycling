from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import DeliveryUnit, BarcodeGenerator

class UnloadInputAPI(View):
    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        prefix = code[:1]

        if prefix == "U":
            try:
                unit = DeliveryUnit.objects.get(barcode__iexact=code)
                return JsonResponse({
                    'type': 'delivery_unit',
                    'delivery_unit_id': unit.id,
                    'customer': unit.delivery.customer.name or None,
                })
            except DeliveryUnit.DoesNotExist:
                return JsonResponse({'error': 'Liefereinheit nicht gefunden'}, status=404)

        elif prefix == "G":
            try:
                reuse = BarcodeGenerator.objects.get(code__iexact=code)
                return JsonResponse({
                    'type': 'reusable',
                    'code': reuse.code,
                    'box_type': reuse.box_type or None,
                    'material': reuse.material_id or None,
                })
            except BarcodeGenerator.DoesNotExist:
                return JsonResponse({'error': 'BarcodeGenerator nicht gefunden'}, status=404)

        return JsonResponse({'error': 'Unbekannter Barcode-Typ'}, status=400)