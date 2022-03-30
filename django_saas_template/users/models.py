from typing import Optional

from core import models as core_models
from django.contrib.auth import models as contrib_models


class SaasUser(
    core_models.TimestampedModel,
    core_models.UuidModel,
    contrib_models.AbstractUser,
):
    @classmethod
    def create(
        cls,
        username: Optional[str] = "",
        email: Optional[str] = "",
        password: Optional[str] = "",
        uuid: Optional[str] = "",
        name: Optional[str] = "",
    ) -> "SaasUser":
        if not (username and email) and not uuid:
            raise ValueError(
                "Couldn't create user: Either username and password, or uuid required."
            )

        return cls.objects.create_user(
            id=uuid,
            username=username or email,
            name=name,
            email=email,
            password=password,
        )
