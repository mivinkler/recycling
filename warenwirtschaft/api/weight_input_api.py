from django.http import JsonResponse
from django.views import View

class WeightInputAPI(View):
    def get(self, request):
        data = request.session.get('unload_input')
        if not data or 'weight' not in data:
            return JsonResponse({'error': 'Kein Gewicht verfügbar'}, status=404)

        weight = data['weight']
        del request.session['unload_input']
        request.session.modified = True

        return JsonResponse({'weight': weight})
