import uuid

from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UuidModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class OrganisationAwareModel(models.Model):
    organisation = models.ForeignKey("Organisation", on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SaasModel(TimestampedModel, UuidModel, OrganisationAwareModel):
    class Meta:
        abstract = True
