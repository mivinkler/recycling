import json
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class UnloadInputAPI(View):
    def post(self, request):
        data = json.loads(request.body)
        weight = data.get('weight')

        if weight is None:
            return JsonResponse({'error': 'Kein Gewicht erhalten'}, status=400)

        request.session['unload_input'] = {
            'weight': weight,
        }
        request.session.modified = True

        return JsonResponse({'status': 'ok'})

