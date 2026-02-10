# warenwirtschaft/api/barcode_recycling_api.py
from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models import Unload


class BarcodeRecyclingAPI(View):
    ACCEPTED_PREFIX = "S"

    def _ok(self, du):
        """Erfolgsantwort vereinheitlichen."""
        return JsonResponse({
            "type": "unload",
            "unload_id": du.id,
            "label": f"Einheit #{du.id}",
        })

    def _err(self, key, status=400, **extra):
        """Fehlerantwort vereinheitlichen."""
        payload = {"ok": False, "error": key}
        payload.update(extra)
        return JsonResponse(payload, status=status)

    def get(self, request):
        # 1) Code einlesen & normalisieren
        code = (request.GET.get("code") or "").strip().upper()
        if not code:
            return self._err("missing_code", 400)

        # 2) Präfix prüfen (Geschäftslogik; KEIN DB-Feld)
        if self.ACCEPTED_PREFIX and not code.startswith(self.ACCEPTED_PREFIX):
            return self._err("wrong_prefix", 400, accepted=self.ACCEPTED_PREFIX)

        # 3) Unload direkt über Barcode suchen
        du = Unload.objects.filter(barcode=code).only("id").first()
        if not du:
            return self._err("not_found", 404)

        return self._ok(du)
