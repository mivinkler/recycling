from django.db import models
from django.db.models import Q


class Material(models.Model):
    SECTION_FIELDS = ("delivery", "unload", "recycling", "halle_zwei")

    name = models.CharField(max_length=50, unique=True)
    delivery = models.BooleanField(default=False)
    unload = models.BooleanField(default=False)
    recycling = models.BooleanField(default=False)
    halle_zwei = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["delivery"]),
            models.Index(fields=["unload"]),
            models.Index(fields=["recycling"]),
            models.Index(fields=["halle_zwei"]),
        ]

    def __str__(self):
        return self.name

    @classmethod
    def for_section(cls, section, *, include=None):
        if section not in cls.SECTION_FIELDS:
            raise ValueError(f"Unsupported material section: {section}")

        filters = Q(**{section: True})
        include_id = getattr(include, "pk", include)

        if include_id is not None:
            filters |= Q(pk=include_id)

        return cls.objects.filter(filters).order_by("name")
