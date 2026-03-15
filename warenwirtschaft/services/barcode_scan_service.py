from django.db.models import Q

from warenwirtschaft.models import BarcodeGenerator, DeliveryUnit, HalleZwei, Recycling, Unload
from warenwirtschaft.models_common.choices import StatusChoices


class BarcodeScanError(ValueError):
    """Ungueltiger oder unvollstaendiger Barcode."""


class BarcodeNotFoundError(LookupError):
    """Zu dem Barcode wurden keine gespeicherten Daten gefunden."""


class BarcodeScanService:
    GENERATED_PREFIX = "G"
    DELIVERY_UNIT_PREFIX = "L"
    UNLOAD_PREFIX = "V"

    @classmethod
    def normalize_barcode(cls, barcode):
        code = (barcode or "").strip().upper()
        if not code:
            raise BarcodeScanError("Kein Barcode uebergeben.")
        return code

    @classmethod
    def ensure_prefix(cls, barcode, prefix):
        if not barcode.startswith(prefix):
            raise BarcodeScanError(f"Nur Barcodes mit {prefix}-Praefix.")

    @classmethod
    def get_generated_prefill_data(cls, barcode):
        code = cls.normalize_barcode(barcode)
        cls.ensure_prefix(code, cls.GENERATED_PREFIX)

        generated = (
            BarcodeGenerator.objects.select_related("customer", "material")
            .filter(barcode__iexact=code)
            .first()
        )
        if generated is None:
            raise BarcodeNotFoundError("BarcodeGenerator nicht gefunden.")

        customer_name = None
        if generated.customer_id:
            customer_name = getattr(generated.customer, "name", str(generated.customer))

        return {
            "type": "generated",
            "barcode": generated.barcode,
            "customer_id": generated.customer_id or None,
            "customer_name": customer_name,
            "delivery_receipt": generated.receipt or None,
            "box_type": generated.box_type or None,
            "material": generated.material_id or None,
            "weight": str(generated.weight) if generated.weight is not None else None,
            "transport": generated.transport or None,
        }

    @classmethod
    def get_shipping_prefill_data(cls, barcode):
        data = cls.get_generated_prefill_data(barcode)

        certificate = None
        receipt = (data.get("delivery_receipt") or "").strip()
        if receipt.isdigit():
            certificate = int(receipt)

        return {
            "type": "generated",
            "barcode": data["barcode"],
            "customer_id": data["customer_id"],
            "customer_name": data["customer_name"],
            "certificate": certificate,
            "transport": data.get("transport"),
        }

    @classmethod
    def _get_delivery_unit_by_barcode(
        cls, barcode, *, allowed_statuses, error_message
    ):
        code = cls.normalize_barcode(barcode)
        cls.ensure_prefix(code, cls.DELIVERY_UNIT_PREFIX)

        delivery_unit = (
            DeliveryUnit.objects.filter(
                barcode__iexact=code,
                status__in=allowed_statuses,
            )
            .only("id", "status")
            .first()
        )
        if delivery_unit is None:
            raise BarcodeNotFoundError(error_message)

        return delivery_unit

    @classmethod
    def _get_unload_by_barcode(cls, barcode, *, allowed_statuses, error_message):
        code = cls.normalize_barcode(barcode)
        cls.ensure_prefix(code, cls.UNLOAD_PREFIX)

        unload = (
            Unload.objects.filter(
                barcode__iexact=code,
                status__in=allowed_statuses,
            )
            .only("id", "status")
            .first()
        )
        if unload is None:
            raise BarcodeNotFoundError(error_message)

        return unload

    @classmethod
    def get_delivery_unit_for_unload(cls, barcode):
        return cls._get_delivery_unit_by_barcode(
            barcode,
            allowed_statuses=[
                StatusChoices.WARTET_AUF_VORSORTIERUNG,
                StatusChoices.AKTIV_IN_VORSORTIERUNG,
            ],
            error_message=(
                "Liefereinheit nicht gefunden oder nicht fuer Vorsortierung bereit."
            ),
        )

    @classmethod
    def get_unload_for_recycling(cls, barcode):
        return cls._get_unload_by_barcode(
            barcode,
            allowed_statuses=[StatusChoices.WARTET_AUF_ZERLEGUNG],
            error_message=(
                "Vorsortierung-Wagen nicht gefunden oder nicht bereit fuer Zerlegung."
            ),
        )

    @classmethod
    def get_delivery_unit_for_halle_zwei(cls, barcode):
        return cls._get_delivery_unit_by_barcode(
            barcode,
            allowed_statuses=[StatusChoices.WARTET_AUF_HALLE_ZWEI],
            error_message=(
                "Liefereinheit nicht gefunden oder nicht bereit fuer Halle 2."
            ),
        )

    @classmethod
    def _ready_or_attached_filter(cls, shipping=None):
        ready_filter = Q(status=StatusChoices.WARTET_AUF_ABHOLUNG, shipping__isnull=True)
        if shipping is None:
            return ready_filter
        return ready_filter | Q(shipping=shipping)

    @classmethod
    def get_shipping_target(cls, barcode, shipping=None):
        code = cls.normalize_barcode(barcode)

        if code.startswith(cls.GENERATED_PREFIX):
            return cls.get_shipping_prefill_data(code)

        unload = (
            Unload.objects.filter(barcode__iexact=code)
            .filter(cls._ready_or_attached_filter(shipping))
            .only("id", "shipping_id", "status")
            .first()
        )
        if unload is not None:
            return {"type": "unload", "id": unload.id}

        recycling = (
            Recycling.objects.filter(barcode__iexact=code)
            .filter(cls._ready_or_attached_filter(shipping))
            .only("id", "shipping_id", "status")
            .first()
        )
        if recycling is not None:
            return {"type": "recycling", "id": recycling.id}

        halle_zwei = (
            HalleZwei.objects.select_related("delivery_unit")
            .filter(delivery_unit__barcode__iexact=code)
            .filter(cls._ready_or_attached_filter(shipping))
            .only("id", "shipping_id", "status", "delivery_unit_id")
            .first()
        )
        if halle_zwei is not None:
            return {"type": "halle_zwei", "id": halle_zwei.id}

        raise BarcodeNotFoundError(
            "Barcode nicht gefunden oder nicht abholbereit."
        )
