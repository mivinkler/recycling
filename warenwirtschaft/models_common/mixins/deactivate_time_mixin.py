# from django.db import models
# from django.utils import timezone


# class DeactivateTimeMixin(models.Model):
#     is_active = models.BooleanField(default=True)
#     inactive_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         abstract = True
#         indexes = [
#             models.Index(fields=["is_active"]),
#         ]

#     def save(self, *args, **kwargs):
#         if not self.is_active and self.inactive_at is None:
#             self.inactive_at = timezone.now()

#         if self.is_active and self.inactive_at is not None:
#             self.inactive_at = None

#         return super().save(*args, **kwargs)
