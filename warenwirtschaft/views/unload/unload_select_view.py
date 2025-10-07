from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse

from warenwirtschaft.forms.unload_form import DeliveryUnitSelectForm
from warenwirtschaft.models import DeliveryUnit, Unload

class UnloadSelectView(View):
    template_name = "unload/unload_select.html"

    def get(self, request):
        # 🇩🇪 Узкий queryset для селекта (без тяжёлых полей/связей)
        du_qs = (DeliveryUnit.objects
                 .filter(status=1)
                 .only("id", "status", "box_type", "weight", "barcode")
                 .order_by("pk"))

        form = DeliveryUnitSelectForm(request.GET or None, queryset=du_qs)

        if "delivery_unit" in request.GET and form.is_valid():
            return self._redirect_by_status(form.cleaned_data["delivery_unit"])

        # 🇩🇪 Для списка Unloads < 20: тонкий запрос, без лишних полей и без N+1 на material
        vorhandene_unloads = (Unload.objects
                              .filter(status__in=[0, 1])  # если 0 реально не используется — поменяй на [1, 2]
                              .order_by("pk")
                              .select_related("material")  # убирает N+1 при {{ u.material }}
                              .only("id", "status", "box_type", "weight", "created_at", "material__name"))

        context = {
            "form": form,
            "vorhandene_unloads": vorhandene_unloads,
            "selected_menu": "unload_create",
        }
        return render(request, self.template_name, context)

    def post(self, request):
        du_qs = (DeliveryUnit.objects
                 .filter(status=1)
                 .only("id", "status", "box_type", "weight", "barcode")
                 .order_by("pk"))
        form = DeliveryUnitSelectForm(request.POST, queryset=du_qs)
        if form.is_valid():
            return self._redirect_by_status(form.cleaned_data["delivery_unit"])
        return render(request, self.template_name, {"form": form})

    def _redirect_by_status(self, du: DeliveryUnit):
        if du.status == 1:
            return redirect(reverse("unload_update", kwargs={"delivery_unit_pk": du.pk}))
        return redirect(reverse("unload_create", kwargs={"delivery_unit_pk": du.pk}))
