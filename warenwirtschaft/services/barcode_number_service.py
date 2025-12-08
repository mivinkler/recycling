import uuid


class BarcodeNumberService:
    """
    Service zur Erzeugung Barcode-Nummern.
    """

    @staticmethod
    def make_code(prefix: str) -> str:
        """
        Erzeugt einen neuen Barcode-String mit Prefix.
        Beispiel: L8F2A9C1B
        """
        return f"{prefix}{uuid.uuid4().hex[:8].upper()}"

    @classmethod
    def set_barcodes(cls, units, prefix: str) -> None:
        """
        Weist Einheiten Barcodes zu, falls diese noch keinen Barcode besitzen.
        Erwartet Objekte mit Attribut 'barcode'.
        """
        for unit in units:
            current = (getattr(unit, "barcode", "") or "").strip()
            if not current:
                unit.barcode = cls.make_code(prefix)

