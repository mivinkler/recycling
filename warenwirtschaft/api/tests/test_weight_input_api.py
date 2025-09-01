# --- Tests für das WeightInputAPI mit Mock der Netzwerkanfrage

from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse

APP_NS = "warenwirtschaft_api"  # --- Namespace aus api/urls.py

class WeightInputAPITest(TestCase):
    def setUp(self):
        # --- Test-Client initialisieren
        self.client = Client()
        self.url = reverse(f"{APP_NS}:weight_input_api")

    # --- Hilfsfunktion – Response-Objekt für urlopen simulieren
    def _mock_urlopen_json(self, payload: bytes):
        resp = MagicMock()
        # Kontextmanager-Protokoll unterstützen: with urlopen(...) as response:
        resp.__enter__.return_value = resp
        # json.load(response) liest aus .read(), also bereitstellen:
        resp.read.return_value = payload
        # Für json.load(response) reicht .read(). Manche Setups lesen .fp/Datei; hier nicht nötig.
        return resp

    @patch("warenwirtschaft.api.weight_input_api.urllib.request.urlopen")
    def test_success_with_netto(self, mock_urlopen):
        # --- Erfolgsfall – Waage liefert JSON mit 'netto'
        mock_urlopen.return_value = self._mock_urlopen_json(b'{"netto": 17.5}')

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content.decode(), {"weight": 17.5})

    @patch("warenwirtschaft.api.weight_input_api.urllib.request.urlopen")
    def test_missing_netto_key(self, mock_urlopen):
        # --- JSON ohne 'netto' führt zu 400
        mock_urlopen.return_value = self._mock_urlopen_json(b'{"brutto": 20}')

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Kein Gewicht", res.json().get("error", ""))

    @patch("warenwirtschaft.api.weight_input_api.urllib.request.urlopen")
    def test_invalid_json_from_scale(self, mock_urlopen):
        # --- Ungültiges JSON (z. B. HTML) -> Exception -> 400
        mock_urlopen.return_value = self._mock_urlopen_json(b"<html>login</html>")

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_mock_query_param(self):
        # --- ?mock=1 gibt immer einen stabilen Testwert zurück
        res = self.client.get(f"{self.url}?mock=1")
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content.decode(), {"weight": 12.34})
