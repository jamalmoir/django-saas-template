from core import models as core_models
from django.db import models


class SaasPlan(core_models.TimestampedModel, core_models.UuidModel):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    stripe_product_id = models.CharField(max_length=255)
