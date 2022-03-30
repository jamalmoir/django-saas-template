from django.contrib.auth.models import AbstractUser

from django_saas_template.core.models import SaasModel


class SaasUser(AbstractUser, SaasModel):
    pass
