from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import ReusableBarcode

class BarcodeDataAPI(View):
    def get(self, request):
        code = request.GET.get("code", "").strip().upper()

        try:
            reusable = ReusableBarcode.objects.get(code__iexact=code)
            return JsonResponse({
                'code': reusable.code,
                'box_type': reusable.box_type,
                'material': reusable.material_id,
                'target': reusable.target,
            })
        except ReusableBarcode.DoesNotExist:

            return JsonResponse({'error': 'Barcode nicht gefunden'}, status=404)

