# warenwirtschaft/api/barcode_shipping_api.py
# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views import View
from warenwirtschaft.models.barcode_generator import BarcodeGenerator
from warenwirtschaft.models import Unload, Recycling  # <- neu

class BarcodeShippingAPI(View):
    def get(self, request):
        # 🇩🇪 Barcode lesen & normalisieren
        code = (request.GET.get("barcode") or "").strip().upper()
        if not code:
            return JsonResponse({"error": "Kein Barcode übergeben."}, status=400)

        pfx = code[:1]

        # ---------- G: Kopf-Felder ----------
        if pfx == "G":
            gen = (BarcodeGenerator.objects
                   .select_related("customer")
                   .filter(barcode__iexact=code)
                   .first())
            if not gen:
                return JsonResponse({"error": "BarcodeGenerator nicht gefunden."}, status=404)

            # receipt → certificate (nur Zahl übernehmen)
            cert_val = None
            if getattr(gen, "receipt", None):
                s = str(gen.receipt).strip()
                if s.isdigit():
                    cert_val = int(s)

            data = {
                "type": "generated",
                "barcode": code,
                "customer_id": getattr(gen, "customer_id", None),
                "customer_name": getattr(gen.customer, "name", None) if getattr(gen, "customer_id", None) else None,
                "certificate": cert_val,
                "transport": getattr(gen, "transport", None),  # 1=Kunde, 2=Eigen
                "note": getattr(gen, "note", None),
            }
            return JsonResponse(data)

        # ---------- S: Unload (abholbereit: status=3, noch nicht versendet) ----------
        if pfx == "S":
            du = (Unload.objects
                  .filter(status=3, shipping__isnull=True, barcode__iexact=code)
                  .only("id")
                  .first())
            if not du:
                return JsonResponse({"error": "Nicht gefunden oder nicht abholbereit.", "where": "unload"}, status=404)
            return JsonResponse({"ok": True, "type": "unload", "id": du.id})

        # ---------- A: Recycling (abholbereit) ----------
        if pfx == "A":
            rec = (Recycling.objects
                   .filter(status=3, shipping__isnull=True, barcode__iexact=code)
                   .only("id")
                   .first())
            if not rec:
                return JsonResponse({"error": "Nicht gefunden oder nicht abholbereit.", "where": "recycling"}, status=404)
            return JsonResponse({"ok": True, "type": "recycling", "id": rec.id})

        # ---------- andere Präfixe ----------
        return JsonResponse({"error": "Falscher Präfix. Erlaubt: G,S,A"}, status=400)
