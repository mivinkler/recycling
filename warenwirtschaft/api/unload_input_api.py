from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import DeliveryUnit, ReusableBarcode

class UnloadInputAPI(View):
    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        barcode_type = request.GET.get("type", "").strip().lower()

        if barcode_type == "unit":
            try:
                unit = DeliveryUnit.objects.get(barcode__iexact=code)
                return JsonResponse({
                    'delivery_unit_id': unit.id,
                    'supplier': unit.delivery.supplier.name,
                })
            except DeliveryUnit.DoesNotExist:
                return JsonResponse({'error': 'DeliveryUnit nicht gefunden'}, status=404)

        elif barcode_type == "reuse":
            try:
                reuse = ReusableBarcode.objects.get(code__iexact=code)
                return JsonResponse({
                    'code': reuse.code,
                    'box_type': reuse.box_type,
                    'material': reuse.material_id,
                    'target': reuse.target,
                })
            except ReusableBarcode.DoesNotExist:
                return JsonResponse({'error': 'ReusableBarcode nicht gefunden'}, status=404)

        return JsonResponse({'error': 'Ungültiger Typ'}, status=400)
