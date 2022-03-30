import json
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework import response, status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny


@api_view(["POST"])
@csrf_exempt
@authentication_classes([])
@permission_classes((AllowAny,))
def user_registered(request):
    given_token = request.headers.get("Authorization", "")

    if not secrets.compare_digest(
        given_token, f"Bearer {settings.USERFRONT_WEBHOOK_API_KEY}"
    ):
        return response.Response(
            status=status.HTTP_401_UNAUTHORIZED, data="Invalid webhook API key."
        )

    user_data = json.loads(request.body).get("record", None)

    if user_data is not None:
        uuid = user_data["uuid"]
        username = user_data["username"]
        name = user_data["name"]
        email = user_data["email"]

        get_user_model().create(uuid=uuid, username=username, name=name, email=email)
    else:
        ValueError("Couldn't create user: No user data provided")

    return response.Response()
