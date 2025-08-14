from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import DeliveryUnit, ReusableBarcode

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
                    'supplier': unit.delivery.supplier.name or None,
                })
            except DeliveryUnit.DoesNotExist:
                return JsonResponse({'error': 'Liefereinheit nicht gefunden'}, status=404)

        elif prefix == "Z":
            try:
                reuse = ReusableBarcode.objects.get(code__iexact=code)
                return JsonResponse({
                    'type': 'reusable',
                    'code': reuse.code,
                    'box_type': reuse.box_type or None,
                    'material': reuse.material_id or None,
                })
            except ReusableBarcode.DoesNotExist:
                return JsonResponse({'error': 'ReusableBarcode nicht gefunden'}, status=404)

        return JsonResponse({'error': 'Unbekannter Barcode-Typ'}, status=400)