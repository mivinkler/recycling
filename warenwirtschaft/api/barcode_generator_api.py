# from django.http import JsonResponse
# from django.views import View
# from warenwirtschaft.models import BarcodeGenerator

# class BarcodeGeneratorAPI(View):
#     def get(self, request):
#         code = request.GET.get("code", "").strip().upper()
#         if not code:
#             return JsonResponse({'error': 'Kein Code übergeben'}, status=400)

#         try:
#             barcode = BarcodeGenerator.objects.get(code__iexact=code)
#             return JsonResponse({
#                 'box_type': barcode.box_type,
#                 'material': barcode.material_id,
#             })
#         except BarcodeGenerator.DoesNotExist:
#             return JsonResponse({'error': 'Nicht gefunden'}, status=404)
