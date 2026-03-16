from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from warenwirtschaft.models import (
    BarcodeGenerator,
    Customer,
    Delivery,
    DeliveryUnit,
    Material,
)
from warenwirtschaft.models_common.choices import BoxTypeChoices


class DeliveryCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("delivery_create")
        self.generated_customer = Customer.objects.create(name="Generated Customer")
        self.manual_customer = Customer.objects.create(name="Manual Customer")
        self.generated_material = Material.objects.create(
            name="Kupfer", delivery=True
        )
        self.manual_material = Material.objects.create(
            name="Aluminium", delivery=True
        )
        self.generated_barcode = BarcodeGenerator.objects.create(
            customer=self.generated_customer,
            receipt="LS-77",
            material=self.generated_material,
            box_type=BoxTypeChoices.GITTERBOX,
            weight=Decimal("12.50"),
            barcode="GTEST123",
        )

    def test_scan_barcode_prefills_empty_fields(self):
        response = self.client.post(
            self.url,
            {
                "scan_barcode": self.generated_barcode.barcode.lower(),
                "customer": "",
                "delivery_receipt": "",
                "b2b": "False",
                "material": "",
                "box_type": "",
                "weight": "",
                "note": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["delivery_form"]["customer"].value(),
            str(self.generated_customer.pk),
        )
        self.assertEqual(
            response.context["delivery_form"]["delivery_receipt"].value(), "LS-77"
        )
        self.assertEqual(
            response.context["unit_form"]["material"].value(),
            str(self.generated_material.pk),
        )
        self.assertEqual(
            response.context["unit_form"]["box_type"].value(),
            str(BoxTypeChoices.GITTERBOX),
        )
        self.assertEqual(response.context["unit_form"]["weight"].value(), "12.50")

    def test_scan_barcode_does_not_override_existing_values(self):
        response = self.client.post(
            self.url,
            {
                "scan_barcode": self.generated_barcode.barcode,
                "customer": str(self.manual_customer.pk),
                "delivery_receipt": "MANUAL-1",
                "b2b": "True",
                "material": str(self.manual_material.pk),
                "box_type": str(BoxTypeChoices.CONTAINER),
                "weight": "99.90",
                "note": "Keep me",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["delivery_form"]["customer"].value(),
            str(self.manual_customer.pk),
        )
        self.assertEqual(
            response.context["delivery_form"]["delivery_receipt"].value(),
            "MANUAL-1",
        )
        self.assertEqual(
            response.context["unit_form"]["material"].value(),
            str(self.manual_material.pk),
        )
        self.assertEqual(
            response.context["unit_form"]["box_type"].value(),
            str(BoxTypeChoices.CONTAINER),
        )
        self.assertEqual(response.context["unit_form"]["weight"].value(), "99.90")
        self.assertEqual(response.context["unit_form"]["note"].value(), "Keep me")

    def test_save_creates_delivery_and_delivery_unit(self):
        response = self.client.post(
            self.url,
            {
                "action": "save",
                "scan_barcode": "",
                "customer": str(self.manual_customer.pk),
                "delivery_receipt": "SAVE-1",
                "b2b": "False",
                "material": str(self.manual_material.pk),
                "box_type": str(BoxTypeChoices.PALETTE),
                "weight": "5.50",
                "note": "Saved unit",
            },
        )

        delivery = Delivery.objects.get()
        delivery_unit = DeliveryUnit.objects.get()

        self.assertRedirects(
            response,
            reverse(
                "delivery_unit_update",
                kwargs={
                    "delivery_pk": delivery.pk,
                    "delivery_unit_pk": delivery_unit.pk,
                },
            ),
        )
        self.assertEqual(delivery.customer, self.manual_customer)
        self.assertEqual(delivery.delivery_receipt, "SAVE-1")
        self.assertEqual(delivery_unit.delivery, delivery)
        self.assertEqual(delivery_unit.material, self.manual_material)
        self.assertEqual(delivery_unit.box_type, BoxTypeChoices.PALETTE)
        self.assertEqual(delivery_unit.weight, Decimal("5.50"))
        self.assertTrue(delivery_unit.barcode.startswith("L"))
