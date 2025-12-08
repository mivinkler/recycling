# from django.views.generic import DetailView
# from warenwirtschaft.models.delivery import Delivery
# from warenwirtschaft.models.delivery_unit import DeliveryUnit

# class DeliveryDetailWeightView(DetailView):
#     model = Delivery
#     template_name = "delivery/delivery_detail_weight.html"
#     context_object_name = "delivery"

#     def get_queryset(self):
#         return super().get_queryset().prefetch_related(
#             "units_for_delivery__delivery",
#             "units_for_delivery__material",
#             "units_for_delivery__unload_for_delivery_unit",
#             "units_for_delivery__unload_for_delivery_unit__recycling_for_unload",
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         delivery_units = self.object.units_for_delivery.all()
        
#         total_item_weight = 0
#         total_unload_weight = 0
#         total_recycling_weight = 0

#         for unit in delivery_units:
#             total_item_weight += unit.weight or 0
#             for unload in unit.unload_for_delivery_unit.all():
#                 total_unload_weight += unload.weight or 0
#                 for recycling in unload.recycling_for_unload.all():
#                     total_recycling_weight += recycling.weight or 0

#         item_diff = total_unload_weight - total_item_weight
#         unload_diff = total_recycling_weight - total_unload_weight

#         context["delivery_units"] = delivery_units
#         context["box_type"] = DeliveryUnit.BOX_TYPE_CHOICES
#         context["statuses"] = DeliveryUnit.STATUS_CHOICES
        
#         context["total_item_weight"] = total_item_weight
#         context["total_unload_weight"] = total_unload_weight
#         context["total_recycling_weight"] = total_recycling_weight
        
#         context["item_diff"] = item_diff
#         context["unload_diff"] = unload_diff
        
#         return context
