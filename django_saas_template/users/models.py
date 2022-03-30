from typing import Optional

from django.contrib.auth.models import AbstractUser
from django_saas_template.core import models as core_models
from django_saas_template.organisations import models as organisation_models


class SaasUser(AbstractUser, core_models.SaasModel):
    @classmethod
    def create(
        cls,
        username: Optional[str] = "",
        email: Optional[str] = "",
        password: Optional[str] = "",
        uuid: Optional[str] = "",
        name: Optional[str] = "",
        organisation_id: Optional[str] = None,
    ) -> "SaasUser":
        if not (username and email) and not uuid:
            raise ValueError(
                "Couldn't create user: Either username and password, or uuid required."
            )

        user = cls.objects.create_user(
            id=uuid,
            username=username or email,
            name=name,
            email=email,
            password=password,
        )
        organisation = organisation_models.Organisation.objects.get(id=organisation_id)

        organisation_models.Member.objects.create(
            organisation=organisation,
            user=user,
        )

        return user
