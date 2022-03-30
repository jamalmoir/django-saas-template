from django_saas_template.core import models as core_models
from django.db import models


class SaasPlan(core_models.SaasModel):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    stripe_product_id = models.CharField(max_length=255)
