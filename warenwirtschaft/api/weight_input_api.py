import json
import urllib.request
from django.http import JsonResponse
from django.views import View

class WeightInputAPI(View):
    def get(self, request):
        try:
            url = 'http://192.168.2.230/waage/waage/stillwiegen'  # ✅ Правильный адрес весов
            with urllib.request.urlopen(url, timeout=3) as response:
                data = json.load(response)
                netto = data.get("netto")
                if netto is not None:
                    return JsonResponse({'weight': netto})
                else:
                    return JsonResponse({'error': 'Kein Gewicht (netto) gefunden'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
