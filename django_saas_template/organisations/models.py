import datetime
from typing import Optional

import sentry_sdk
from core import models as core_models
from django.db import models
from django.utils import timezone
from djstripe import models as djstripe_models
from subscriptions import models as subscription_models
from users import models as user_models


class Organisation(core_models.TimestampedModel, core_models.UuidModel):
    name = models.CharField(max_length=100)
    image = models.URLField()
    owner = models.ForeignKey(
        "Member",
        on_delete=models.PROTECT,
        related_name="owned_organisations",
    )

    @property
    def email(self):
        return self.owner.user.email

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
        name: str,
        tenant_id: str,
        owner_user: user_models.SaasUser,
        image: Optional[str] = "",
    ) -> "Organisation":
        organisation = cls.objects.create(
            id=tenant_id,
            name=name,
            image=image,
        )

        # Create and set the owner Member.
        owner_member = Member.objects.create(organisation=organisation, user=owner_user)
        organisation.owner = owner_member
        organisation.save()

        # Create organisation's settings and set their trial to 30 days in the future.
        OrganisationSettings.objects.create(
            organisation=organisation,
            trials_ends_at=timezone.now() + datetime.timedelta(days=30),
        )

        # Create a customer for the organisation in Stripe.
        customer, _ = djstripe_models.Customer.get_or_create(subscriber=organisation)

        return organisation


class OrganisationSettings(core_models.TimestampedModel, core_models.UuidModel):
    organisation = models.OneToOneField(
        Organisation, on_delete=models.CASCADE, related_name="settings"
    )
    trials_ends_at = models.DateTimeField()


class Member(core_models.TimestampedModel, core_models.UuidModel):
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        user_models.SaasUser, on_delete=models.CASCADE, related_name="memberships"
    )
