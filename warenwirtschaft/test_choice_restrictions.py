from django.test import TestCase
from django.urls import reverse

from warenwirtschaft.forms.recycling_form import (
    RECYCLING_FORM_BOX_TYPE_CHOICES,
    RECYCLING_FORM_STATUS_CHOICES,
)
from warenwirtschaft.models import Material, Recycling, Unload
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
