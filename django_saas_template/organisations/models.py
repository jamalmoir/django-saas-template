import datetime
from typing import Optional

import sentry_sdk
from django.db import models
from django.utils import timezone
from django_saas_template.core import models as core_models
from django_saas_template.subscriptions import models as subscription_models
from django_saas_template.users import models as useer_models
from djstripe import models as djstripe_models


class Organisation(core_models.TimestampedModel, core_models.UuidModel):
    name = models.CharField(max_length=100)
    image = models.URLField()

    @property
    def customer(self) -> djstripe_models.Customer:
        return self.djstripe_customers.get()

    @property
    def subscription(self) -> Optional[subscription_models.SaasPlan]:
        product_id = (
            self.customer.subscription.plan.product_id
            if self.customer.subscription
            else None
        )

        if product_id is None and self.settings.trials_ends_at >= timezone.now():
            product_id = "trial"

        if product_id is not None:
            try:
                return subscription_models.SaasPlan.objects.get(
                    stripe_product_id=product_id
                )
            except subscription_models.SaasPlan.DoesNotExist as e:
                sentry_sdk.capture_exception(e)
                return None
        else:
            return None

    @classmethod
    def create(
        cls,
        name: Optional[str] = "",
        tenant_id: Optional[str] = "",
        image: Optional[str] = "",
    ) -> "Organisation":
        organisation = cls.objects.create(
            id=tenant_id,
            name=name,
            image=image,
        )

        # Create organisation's settings and set their trial to 30 days in the future.
        OrganisationSettings.objects.create(
            organisation=organisation,
            trials_ends_at=timezone.now() + datetime.timedelta(days=30),
        )

        # Create a customer for the organisation in Stripe
        customer, _ = djstripe_models.Customer.get_or_create(subscriber=organisation)

        return organisation


class OrganisationSettings(core_models.TimestampedModel, core_models.UuidModel):
    organisation = models.OneToOneField(
        Organisation, on_delete=models.CASCADE, related_name="settings"
    )
    trials_ends_at = models.DateTimeField(null=True, blank=True)


class Member(core_models.TimestampedModel, core_models.UuidModel):
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        useer_models.SaasUser, on_delete=models.CASCADE, related_name="memberships"
    )
