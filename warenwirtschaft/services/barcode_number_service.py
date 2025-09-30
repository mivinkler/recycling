import uuid

class BarcodeNumberService:
    """
    Service zur Erzeugung von Barcode-Nummern mit Prefix.
    Beispiel: L8F2A9C1B (L = Lieferungen, S = Unloads, A = Recycling, G = Generator)
    """
    @staticmethod
    def make_code(prefix: str) -> str:
        suffix = uuid.uuid4().hex[:8].upper()
        return f"{prefix}{suffix}"
