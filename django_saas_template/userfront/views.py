import json
import secrets
from typing import Any, Dict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django_saas_template.organisations import models as organisation_models
from django_saas_template.userfront import dataclasses
from django_saas_template.users import models as user_models
from rest_framework import response, status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny


@api_view(["POST"])
@csrf_exempt
@authentication_classes([])
@permission_classes((AllowAny,))
def webhook(request):
    given_token = request.headers.get("Authorization", "")

    if not secrets.compare_digest(
        given_token, f"Bearer {settings.USERFRONT_WEBHOOK_API_KEY}"
    ):
        return response.Response(
            status=status.HTTP_401_UNAUTHORIZED, data="Invalid webhook API key."
        )

    data = json.loads(request.body)
    action = data.get("action")
    model = data.get("model")
    record = data.get("record")

    if record is None:
        ValueError("Couldn't process UserFront webhook: No record data provided")

    process_webhook(action=action, model=model, record=record)

    return response.Response()


def process_webhook(action: str, model: str, record: Dict[str, Any]) -> None:
    match model:
        case "user":
            match action:
                case "create":
                    create_user(user_data=record)
                case "update":
                    update_user(user_data=record)
                case "delete":
                    delete_user(user_data=record)
                case _:
                    raise ValueError(
                        "Couldn't process UserFront webhook: Invalid action"
                    )
        case "tenant":
            match action:
                case "create":
                    create_tenant(tenant_data=record)
                case "update":
                    update_tenant(tenant_data=record)
                case "delete":
                    delete_tenant(tenant_data=record)
                case _:
                    raise ValueError(
                        "Couldn't process UserFront webhook: Invalid action"
                    )
        case _:
            raise ValueError("Couldn't process UserFront webhook: Invalid model")


def extract_user(user_data: Dict[str, Any]) -> dataclasses.UserfrontUser:
    return dataclasses.UserfrontUser(
        uuid=user_data["uuid"],
        tenant_id=user_data["tenantId"],
        username=user_data["username"],
        name=user_data["name"],
        email=user_data["email"],
        image=user_data["image"],
    )


def extract_tenant(tenant_data: Dict[str, Any]) -> dataclasses.UserfrontTenant:
    return dataclasses.UserfrontTenant(
        tenant_id=tenant_data["tenantId"],
        name=tenant_data["name"],
        image=tenant_data["image"],
    )


def create_user(user_data: Dict[str, Any]):
    user = extract_user(user_data=user_data)
    get_user_model().create(
        uuid=user.uuid,
        organisation_id=user.tenant_id,
        username=user.username,
        name=user.name,
        email=user.email,
    )


def update_user(user_data: Dict[str, Any]):
    userfront_user = extract_user(user_data=user_data)
    user = user_models.SaasUser.objects.get(id=userfront_user.uuid)

    user.username = userfront_user.username
    user.name = userfront_user.name
    user.email = userfront_user.email

    user.save()


def delete_user(user_data: Dict[str, Any]):
    userfront_user = extract_user(user_data=user_data)
    user = user_models.SaasUser.objects.get(id=userfront_user.uuid)
    user.delete()


def create_tenant(tenant_data: Dict[str, Any]):
    tenant = extract_tenant(tenant_data=tenant_data)
    organisation_models.Organisation.create(
        tenant_id=tenant.tenant_id,
        name=tenant.name,
        image=tenant.image,
    )


def update_tenant(tenant_data: Dict[str, Any]):
    userfront_tenant = extract_tenant(tenant_data=tenant_data)
    organisation = organisation_models.Organisation.objects.get(
        id=userfront_tenant.tenant_id
    )

    organisation.name = userfront_tenant.name
    organisation.image = userfront_tenant.image

    organisation.save()


def delete_tenant(tenant_data: Dict[str, Any]):
    userfront_tenant = extract_tenant(tenant_data=tenant_data)
    organisation = organisation_models.Organisation.objects.get(
        id=userfront_tenant.tenant_id
    )
    organisation.delete()
