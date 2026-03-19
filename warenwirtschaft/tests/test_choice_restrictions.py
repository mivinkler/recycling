from django.test import TestCase
from django.urls import reverse

from warenwirtschaft.forms.delivery_form import DeliveryUnitForm
from warenwirtschaft.forms.recycling_form import (
    RECYCLING_FORM_BOX_TYPE_CHOICES,
    RECYCLING_FORM_STATUS_CHOICES,
    RecyclingForm,
)
from warenwirtschaft.forms.unload_form import UnloadForm
from warenwirtschaft.models import DeliveryUnit, Material, Recycling, Unload
from warenwirtschaft.models_common.choices import BoxTypeChoices, StatusChoices


class ChoiceRestrictionTests(TestCase):
    def _get_filter(self, response, field_name):
        return next(
            search_filter
            for search_filter in response.context["search_filters"]
            if search_filter["field"] == field_name
        )

    def test_unload_list_status_filter_excludes_waiting_for_unload(self):
        response = self.client.get(reverse("unload_list"))

        status_filter = self._get_filter(response, "status")
        status_values = {choice["value"] for choice in status_filter["choices"]}

        self.assertNotIn(str(StatusChoices.WARTET_AUF_VORSORTIERUNG), status_values)
        self.assertIn(str(StatusChoices.AKTIV_IN_VORSORTIERUNG), status_values)
        self.assertIn(str(StatusChoices.ERLEDIGT), status_values)

    def test_recycling_list_filters_use_restricted_statuses_and_box_types(self):
        response = self.client.get(reverse("recycling_list"))

        status_filter = self._get_filter(response, "status")
        status_values = {choice["value"] for choice in status_filter["choices"]}
        self.assertEqual(
            status_values,
            {
                str(StatusChoices.AKTIV_IN_ZERLEGUNG),
                str(StatusChoices.WARTET_AUF_ABHOLUNG),
                str(StatusChoices.ERLEDIGT),
            },
        )

        box_type_filter = self._get_filter(response, "box_type")
        box_type_values = {choice["value"] for choice in box_type_filter["choices"]}
        self.assertNotIn(str(BoxTypeChoices.CONTAINER), box_type_values)
        self.assertIn(str(BoxTypeChoices.GITTERBOX), box_type_values)
        self.assertIn(str(BoxTypeChoices.OHNE_BEHAELTER), box_type_values)

    def test_delivery_form_status_choices_are_restricted_to_purpose_values(self):
        form = DeliveryUnitForm()
        status_values = {value for value, _ in form.fields["status"].choices}
        self.assertEqual(
            status_values,
            {
                StatusChoices.WARTET_AUF_VORSORTIERUNG,
                StatusChoices.WARTET_AUF_HALLE_ZWEI,
            },
        )

    def test_unload_form_status_choices_exclude_halle_zwei(self):
        form = UnloadForm()
        status_values = {value for value, _ in form.fields["status"].choices}
        self.assertNotIn(StatusChoices.WARTET_AUF_HALLE_ZWEI, status_values)
        self.assertEqual(
            status_values,
            {
                StatusChoices.WARTET_AUF_ZERLEGUNG,
                StatusChoices.WARTET_AUF_ABHOLUNG,
            },
        )

    def test_recycling_create_shows_active_and_ready_items_with_restricted_form_choices(self):
        material = Material.objects.create(name="Recycling Material", recycling=True, unload=True)
        active_recycling = Recycling.objects.create(
            material=material,
            box_type=BoxTypeChoices.GITTERBOX,
            weight="12.00",
            status=StatusChoices.AKTIV_IN_ZERLEGUNG,
        )
        ready_recycling = Recycling.objects.create(
            material=material,
            box_type=BoxTypeChoices.PALETTE,
            weight="10.00",
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
        )
        Recycling.objects.create(
            material=material,
            box_type=BoxTypeChoices.WAGEN,
            weight="8.00",
            status=StatusChoices.ERLEDIGT,
        )

        response = self.client.get(reverse("recycling_create"))

        visible_ids = {recycling.pk for recycling in response.context["recyclings"]}
        self.assertIn(active_recycling.pk, visible_ids)
        self.assertIn(ready_recycling.pk, visible_ids)
        self.assertEqual(
            response.context["new_form"].fields["status"].choices,
            RECYCLING_FORM_STATUS_CHOICES,
        )
        self.assertEqual(
            response.context["new_form"].fields["box_type"].choices,
            RECYCLING_FORM_BOX_TYPE_CHOICES,
        )

    def test_material_forms_only_allow_materials_from_their_section(self):
        delivery_material = Material.objects.create(name="Delivery", delivery=True)
        unload_material = Material.objects.create(name="Unload", unload=True)
        recycling_material = Material.objects.create(name="Recycling", recycling=True)

        delivery_form = DeliveryUnitForm()
        self.assertEqual(
            set(delivery_form.fields["material"].queryset.values_list("pk", flat=True)),
            {delivery_material.pk},
        )

        unload_form = UnloadForm()
        self.assertEqual(
            set(unload_form.fields["material"].queryset.values_list("pk", flat=True)),
            {unload_material.pk},
        )

        recycling_form = RecyclingForm()
        self.assertEqual(
            set(recycling_form.fields["material"].queryset.values_list("pk", flat=True)),
            {recycling_material.pk},
        )

    def test_material_forms_keep_current_material_during_edit_even_if_flag_was_removed(self):
        current_delivery_material = Material.objects.create(name="Legacy Delivery")
        current_unload_material = Material.objects.create(name="Legacy Unload")
        current_recycling_material = Material.objects.create(name="Legacy Recycling")
        shared_material = Material.objects.create(
            name="Shared",
            delivery=True,
            unload=True,
            recycling=True,
        )

        delivery_form = DeliveryUnitForm(
            instance=DeliveryUnit(material=current_delivery_material)
        )
        self.assertEqual(
            set(delivery_form.fields["material"].queryset.values_list("pk", flat=True)),
            {current_delivery_material.pk, shared_material.pk},
        )

        unload_form = UnloadForm(instance=Unload(material=current_unload_material))
        self.assertEqual(
            set(unload_form.fields["material"].queryset.values_list("pk", flat=True)),
            {current_unload_material.pk, shared_material.pk},
        )

        recycling_form = RecyclingForm(
            instance=Recycling(material=current_recycling_material)
        )
        self.assertEqual(
            set(recycling_form.fields["material"].queryset.values_list("pk", flat=True)),
            {current_recycling_material.pk, shared_material.pk},
        )

    def test_material_filters_in_lists_only_show_materials_for_the_current_section(self):
        delivery_material = Material.objects.create(name="Delivery", delivery=True)
        unload_material = Material.objects.create(name="Unload", unload=True)
        recycling_material = Material.objects.create(name="Recycling", recycling=True)
        shared_material = Material.objects.create(
            name="Shared",
            delivery=True,
            unload=True,
            recycling=True,
        )

        delivery_response = self.client.get(reverse("delivery_list"))
        delivery_filter = self._get_filter(delivery_response, "material__name")
        self.assertEqual(
            {choice["value"] for choice in delivery_filter["choices"]},
            {str(delivery_material.pk), str(shared_material.pk)},
        )

        unload_response = self.client.get(reverse("unload_list"))
        unload_filter = self._get_filter(unload_response, "material__name")
        self.assertEqual(
            {choice["value"] for choice in unload_filter["choices"]},
            {str(unload_material.pk), str(shared_material.pk)},
        )

        recycling_response = self.client.get(reverse("recycling_list"))
        recycling_filter = self._get_filter(recycling_response, "material__name")
        self.assertEqual(
            {choice["value"] for choice in recycling_filter["choices"]},
            {str(recycling_material.pk), str(shared_material.pk)},
        )

    def test_shipping_list_renders_barcode_filter(self):
        response = self.client.get(reverse("shipping_list"))

        barcode_filter = self._get_filter(response, "barcode")
        self.assertEqual(barcode_filter["label"], "Barcode")
        self.assertContains(response, 'name="barcode"')

    def test_material_forms_reject_materials_from_other_sections(self):
        wrong_delivery_material = Material.objects.create(name="Wrong Delivery", unload=True)
        wrong_unload_material = Material.objects.create(name="Wrong Unload", recycling=True)
        wrong_recycling_material = Material.objects.create(name="Wrong Recycling", delivery=True)

        delivery_form = DeliveryUnitForm(data={"material": wrong_delivery_material.pk})
        self.assertFalse(delivery_form.is_valid())
        self.assertIn("material", delivery_form.errors)

        unload_form = UnloadForm(
            data={
                "material": wrong_unload_material.pk,
                "status": str(StatusChoices.WARTET_AUF_ZERLEGUNG),
            }
        )
        self.assertFalse(unload_form.is_valid())
        self.assertIn("material", unload_form.errors)

        recycling_form = RecyclingForm(
            data={
                "material": wrong_recycling_material.pk,
                "status": str(StatusChoices.AKTIV_IN_ZERLEGUNG),
            }
        )
        self.assertFalse(recycling_form.is_valid())
        self.assertIn("material", recycling_form.errors)

    def test_recycling_update_uses_the_same_restricted_choices(self):
        material = Material.objects.create(name="Update Material", recycling=True, unload=True)
        recycling = Recycling.objects.create(
            material=material,
            box_type=BoxTypeChoices.GITTERBOX,
            weight="12.00",
            status=StatusChoices.AKTIV_IN_ZERLEGUNG,
        )

        response = self.client.get(
            reverse("recycling_update", kwargs={"recycling_pk": recycling.pk})
        )

        self.assertEqual(
            response.context["form"].fields["status"].choices,
            RECYCLING_FORM_STATUS_CHOICES,
        )
        self.assertEqual(
            response.context["form"].fields["box_type"].choices,
            RECYCLING_FORM_BOX_TYPE_CHOICES,
        )
        self.assertEqual(
            response.context["new_form"].fields["status"].choices,
            RECYCLING_FORM_STATUS_CHOICES,
        )
        self.assertEqual(
            response.context["new_form"].fields["box_type"].choices,
            RECYCLING_FORM_BOX_TYPE_CHOICES,
        )

    def test_recycling_create_attaches_unload_only_to_in_progress_recyclings(self):
        material = Material.objects.create(name="Attach Material", recycling=True, unload=True)
        active_recycling = Recycling.objects.create(
            material=material,
            box_type=BoxTypeChoices.GITTERBOX,
            weight="12.00",
            status=StatusChoices.AKTIV_IN_ZERLEGUNG,
        )
        ready_recycling = Recycling.objects.create(
            material=material,
            box_type=BoxTypeChoices.PALETTE,
            weight="10.00",
            status=StatusChoices.WARTET_AUF_ABHOLUNG,
        )
        unload = Unload.objects.create(
            material=material,
            box_type=BoxTypeChoices.WAGEN,
            weight="15.00",
            status=StatusChoices.WARTET_AUF_ZERLEGUNG,
        )

        response = self.client.post(
            reverse("recycling_create"),
            {"unload_id": str(unload.pk)},
        )

        self.assertRedirects(response, reverse("recycling_create"))
        self.assertIn(unload, active_recycling.unloads.all())
        self.assertNotIn(unload, ready_recycling.unloads.all())
