from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from warenwirtschaft.models.material import Material

class MaterialUpdateView(View):
    template_name = "material/material_update.html"

    def get(self, request, pk):
        context = {
            "material_list": Material.objects.all(),
            "edit_material": get_object_or_404(Material, pk=pk),
            "selected_menu": "material_form"
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        material = get_object_or_404(Material, pk=pk)

        material.name = request.POST.get("name", material.name)

        material.delivery  = "delivery"  in request.POST
        material.unload    = "unload"    in request.POST
        material.recycling = "recycling" in request.POST
        material.device_check = "device_check" in request.POST

        material.save()
        return redirect("material_create")
