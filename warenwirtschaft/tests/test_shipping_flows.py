from django.test import TestCase
from django.urls import reverse

from warenwirtschaft.models import (
    BarcodeGenerator,
    Customer,
    Delivery,
    DeliveryUnit,
    HalleZwei,
    Material,
    Recycling,
    Shipping,
    Unload,
)
from warenwirtschaft.models_common.choices import BoxTypeChoices, StatusChoices, TransportChoices


class ShippingFlowTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Shipping Customer")
        self.other_customer = Customer.objects.create(name="Generated Shipping Customer")
        self.material = Material.objects.create(name="Shipping Material", delivery=True)

        self.delivery = Delivery.objects.create(
            customer=self.customer,
            delivery_receipt="D-1",
        )
        self.delivery_unit = DeliveryUnit.objects.create(
            delivery=self.delivery,
            material=self.material,
            box_type=BoxTypeChoices.GITTERBOX,
            weight="15.50",
            status=StatusChoices.ERLEDIGT,
            barcode="LHALLE900",
        )
        self.halle_zwei = HalleZwei.objects.create(
            delivery_unit=self.delivery_unit,
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            halle_zwei=True,
        )
        self.unload = Unload.objects.create(
            material=self.material,
            box_type=BoxTypeChoices.CONTAINER,
            weight="25.00",
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
            barcode="VSHIP100",
        )
        self.generated = BarcodeGenerator.objects.create(
            customer=self.other_customer,
            receipt="12345",
            transport=TransportChoices.EIGEN,
            barcode="GSHIP100",
        )

    def test_shipping_create_scan_generated_prefills_header(self):
        response = self.client.post(
            reverse("shipping_create"),
            {
                "action": "scan_barcode",
                "scan_barcode": self.generated.barcode,
                "customer": "",
                "certificate": "",
                "transport": "",
                "note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"]["customer"].value(),
            str(self.other_customer.pk),
        )
        self.assertEqual(response.context["form"]["certificate"].value(), "12345")
        self.assertEqual(
            response.context["form"]["transport"].value(),
            str(TransportChoices.EIGEN),
        )

    def test_shipping_create_requires_at_least_one_selected_entry(self):
        response = self.client.post(
            reverse("shipping_create"),
            {
                "customer": str(self.customer.pk),
                "certificate": "777",
                "transport": str(TransportChoices.KUNDE),
                "note": "Created",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Bitte mindestens einen Eintrag aus &#x27;Abholbereit / Zugeordnet&#x27; auswaehlen.",
        )
        self.assertFalse(Shipping.objects.exists())

    def test_shipping_create_scan_ready_unload_preselects_item_without_saving(self):
        response = self.client.post(
            reverse("shipping_create"),
            {
                "action": "scan_barcode",
                "scan_barcode": self.unload.barcode,
                "customer": str(self.customer.pk),
                "certificate": "100",
                "transport": str(TransportChoices.KUNDE),
                "note": "Scan attach",
            },
        )

        self.unload.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Shipping.objects.exists())
        self.assertIn(self.unload.pk, response.context["preselected_unload_ids"])
        self.assertIsNone(self.unload.shipping)
        self.assertEqual(self.unload.status, StatusChoices.WARTET_AUF_ABHOLUNG)
        self.assertIsNone(self.unload.inactive_at)

    def test_shipping_create_save_sets_selected_items_done_and_inactive_at(self):
        response = self.client.post(
            reverse("shipping_create"),
            {
                "customer": str(self.customer.pk),
                "certificate": "100",
                "transport": str(TransportChoices.KUNDE),
                "note": "Finished loading",
                "selected_unload": str(self.unload.pk),
            },
        )

        shipping = Shipping.objects.get()
        self.unload.refresh_from_db()

        self.assertRedirects(response, reverse("shipping_create"))
        self.assertEqual(self.unload.shipping, shipping)
        self.assertEqual(self.unload.status, StatusChoices.ERLEDIGT)
        self.assertIsNotNone(self.unload.inactive_at)

    def test_shipping_update_scan_halle_zwei_delivery_unit_barcode_links_item(self):
        shipping = Shipping.objects.create(
            customer=self.customer,
            certificate=88,
            transport=TransportChoices.KUNDE,
        )

        response = self.client.post(
            reverse("shipping_update", kwargs={"pk": shipping.pk}),
            {
                "action": "scan_barcode",
                "scan_barcode": self.delivery_unit.barcode,
                "customer": str(shipping.customer_id),
                "certificate": str(shipping.certificate),
                "transport": str(shipping.transport),
                "note": shipping.note or "",
            },
        )

        self.halle_zwei.refresh_from_db()
        self.assertRedirects(
            response,
            reverse("shipping_update", kwargs={"pk": shipping.pk}),
        )
        self.assertEqual(self.halle_zwei.shipping_id, shipping.pk)
        self.assertEqual(self.halle_zwei.status, StatusChoices.ERLEDIGT)
        self.assertIsNotNone(self.halle_zwei.inactive_at)

    def test_shipping_update_requires_at_least_one_selected_entry(self):
        shipping = Shipping.objects.create(
            customer=self.customer,
            certificate=89,
            transport=TransportChoices.KUNDE,
        )

        response = self.client.post(
            reverse("shipping_update", kwargs={"pk": shipping.pk}),
            {
                "customer": str(shipping.customer_id),
                "certificate": str(shipping.certificate),
                "transport": str(shipping.transport),
                "note": shipping.note or "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Bitte mindestens einen Eintrag aus &#x27;Abholbereit / Zugeordnet&#x27; auswaehlen.",
        )

    def test_shipping_create_renders_halle_zwei_values_from_delivery_unit(self):
        response = self.client.get(reverse("shipping_create"))

        self.assertContains(response, "Shipping Material")
        self.assertContains(response, "Gitterbox")
        self.assertContains(response, "15,50")

    def test_recycling_marked_as_ready_appears_in_shipping_create(self):
        recycling = Recycling.objects.create(
            material=self.material,
            box_type=BoxTypeChoices.GITTERBOX,
            weight="11.00",
            status=StatusChoices.AKTIV_IN_ZERLEGUNG,
            note="Ready for pickup",
        )

        response = self.client.post(
            reverse("recycling_update", kwargs={"recycling_pk": recycling.pk}),
            {
                "material": str(self.material.pk),
                "box_type": str(BoxTypeChoices.GITTERBOX),
                "weight": "11.00",
                "status": str(StatusChoices.WARTET_AUF_ABHOLUNG),
                "note": "Ready for pickup",
                "new_weight": "",
            },
        )

        self.assertRedirects(response, reverse("recycling_create"))

        recycling.refresh_from_db()
        self.assertEqual(recycling.status, StatusChoices.WARTET_AUF_ABHOLUNG)

        shipping_response = self.client.get(reverse("shipping_create"))
        self.assertContains(shipping_response, "Shipping Material")
        self.assertContains(shipping_response, "11,00")
