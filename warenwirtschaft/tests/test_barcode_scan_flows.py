from django.test import TestCase
from django.urls import reverse

from warenwirtschaft.models import (
    Customer,
    Delivery,
    DeliveryUnit,
    HalleZwei,
    Material,
    Recycling,
    Unload,
)
from warenwirtschaft.models_common.choices import StatusChoices


class BarcodeScanFlowTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Scan Customer")
        self.material = Material.objects.create(name="Scan Material", delivery=True)
        self.delivery = Delivery.objects.create(
            customer=self.customer,
            delivery_receipt="SCAN-1",
        )

    def _create_delivery_unit(self, *, barcode, status):
        return DeliveryUnit.objects.create(
            delivery=self.delivery,
            material=self.material,
            weight="10.00",
            status=status,
            barcode=barcode,
        )

    def test_unload_select_scan_redirects_for_ready_and_active_delivery_units(self):
        ready_unit = self._create_delivery_unit(
            barcode="LREADY001",
            status=StatusChoices.WARTET_AUF_VORSORTIERUNG,
        )
        active_unit = self._create_delivery_unit(
            barcode="LACTIVE01",
            status=StatusChoices.AKTIV_IN_VORSORTIERUNG,
        )

        ready_response = self.client.post(
            reverse("unload_select"),
            {"scan_barcode": ready_unit.barcode},
        )
        active_response = self.client.post(
            reverse("unload_select"),
            {"scan_barcode": active_unit.barcode},
        )

        self.assertRedirects(
            ready_response,
            reverse("unload_create", kwargs={"delivery_unit_pk": ready_unit.pk}),
        )
        self.assertRedirects(
            active_response,
            reverse("unload_create", kwargs={"delivery_unit_pk": active_unit.pk}),
        )

    def test_recycling_scan_matches_add_button_behavior(self):
        unload = Unload.objects.create(
            material=self.material,
            weight="5.00",
            status=StatusChoices.WARTET_AUF_ZERLEGUNG,
            barcode="VREADY001",
        )
        recycling_one = Recycling.objects.create(
            material=self.material,
            weight="1.00",
            status=StatusChoices.AKTIV_IN_ZERLEGUNG,
        )
        recycling_two = Recycling.objects.create(
            material=self.material,
            weight="2.00",
            status=StatusChoices.AKTIV_IN_ZERLEGUNG,
        )

        response = self.client.post(
            reverse("recycling_create"),
            {
                "action": "scan_unload",
                "scan_barcode": unload.barcode,
            },
        )

        unload.refresh_from_db()
        recycling_one.refresh_from_db()
        recycling_two.refresh_from_db()

        self.assertRedirects(response, reverse("recycling_create"))
        self.assertEqual(unload.status, StatusChoices.ERLEDIGT)
        self.assertIsNotNone(unload.inactive_at)
        self.assertIn(unload, recycling_one.unloads.all())
        self.assertIn(unload, recycling_two.unloads.all())

    def test_halle_zwei_scan_matches_check_behavior(self):
        delivery_unit = self._create_delivery_unit(
            barcode="LHALLE001",
            status=StatusChoices.WARTET_AUF_HALLE_ZWEI,
        )

        response = self.client.post(
            reverse("halle_zwei_create"),
            {
                "action": "scan_check",
                "scan_barcode": delivery_unit.barcode,
            },
        )

        delivery_unit.refresh_from_db()
        halle_zwei = HalleZwei.objects.get(delivery_unit=delivery_unit)

        self.assertRedirects(response, reverse("halle_zwei_create"))
        self.assertEqual(delivery_unit.status, StatusChoices.ERLEDIGT)
        self.assertIsNotNone(delivery_unit.inactive_at)
        self.assertEqual(halle_zwei.status, StatusChoices.WARTET_AUF_ABHOLUNG)
        self.assertTrue(halle_zwei.halle_zwei)
