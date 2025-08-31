from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import BarcodeGenerator


class DeliveryInputAPI(View):
    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        prefix = code[:1]

        if prefix != "L":
            return JsonResponse({'error': 'Nur Barcodes mit L-Präfix sind für Wareneingang gültig.'}, status=400)

        try:
            reuse = BarcodeGenerator.objects.get(code__iexact=code)

            return JsonResponse({
                'type': 'delivery_unit_reuse',
                'code': reuse.code,
                'box_type': reuse.box_type or None,
                'material': reuse.material_id or None,
                'area': reuse.area or None,
                'customer': reuse.customer_id if reuse.customer_id else None,
                'delivery_receipt': reuse.delivery_receipt or None,
            })
        except BarcodeGenerator.DoesNotExist:
            return JsonResponse({'error': 'BarcodeGenerator nicht gefunden'}, status=404)

