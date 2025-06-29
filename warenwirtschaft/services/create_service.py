# # warenwirtschaft/views/mixins/base_unit_create_view.py
# import uuid
# from django.views.generic.edit import CreateView
# from django.db import transaction
# from django.shortcuts import redirect

# from warenwirtschaft.services.barcode_service import BarcodeGenerator


# class CreateService(CreateView):
#     """
#     Abstrakte Klasse für CreateViews, die mehrere Einheiten mit Barcode generieren.
#     Muss folgende Attribute setzen:
#     - form_class
#     - formset_class
#     - code_prefix ('L' oder 'U')
#     - barcode_path (zB. 'barcodes/delivery')
#     """
#     form_class = None
#     formset_class = None
#     code_prefix = None
#     barcode_path = None
#     form_key = "form"
#     formset_key = "formset"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         post_data = self.request.POST or None

#         if self.form_class:
#             context[self.form_key] = self.form_class(post_data)
#         context[self.formset_key] = self.formset_class(post_data, prefix=self.formset_key)
#         context["empty_form"] = context[self.formset_key].empty_form
#         return context

#     def post(self, request, *args, **kwargs):
#         context = self.get_context_data()
#         main_form = context.get(self.form_key)
#         formset = context[self.formset_key]

#         if (not self.form_class or main_form.is_valid()) and formset.is_valid():
#             with transaction.atomic():
#                 if self.form_class:
#                     self.object = main_form.save()
#                     formset.instance = self.object

#                 units = formset.save(commit=False)
#                 for unit in units:
#                     suffix = uuid.uuid4().hex[:8].upper()
#                     code = f"{self.code_prefix}{suffix}"
#                     if hasattr(unit, "code"):
#                         unit.code = code
#                     else:
#                         unit.barcode = code

#                     BarcodeGenerator(unit, code, self.barcode_path).generate_image()
#                     unit.save()

#             return redirect(self.get_success_url())

#         return self.render_to_response(context)
