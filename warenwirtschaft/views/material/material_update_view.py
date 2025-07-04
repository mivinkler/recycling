from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from warenwirtschaft.models.material import Material

class MaterialUpdateView(View):
    template_name = "material/material_update.html"

    def get(self, request, pk):
        context = {
            "material_list": Material.objects.all(),
            "edit_material": get_object_or_404(Material, pk=pk),
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        name = request.POST.get("name")
        if name:
            Material.objects.filter(pk=pk).update(name=name)
        return redirect("material_list")
