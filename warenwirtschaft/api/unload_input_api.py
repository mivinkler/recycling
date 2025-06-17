from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import DeliveryUnit

class UnloadInputAPI(View):
    def get(self, request):
        code = request.GET.get("code", "").strip().upper()
        if not code:
            return JsonResponse({'error': 'Kein Code übergeben'}, status=400)

        try:
            unit = DeliveryUnit.objects.get(barcode__iexact=code)
            return JsonResponse({
                'delivery_unit_id': unit.id,
                'supplier': unit.delivery.supplier.name,
            })
        except DeliveryUnit.DoesNotExist:
            return JsonResponse({'error': 'Nicht gefunden'}, status=404)
