from django.urls import path
from django_saas_template.userfront import views

urlpatterns = [path("userfront/webhook/", views.webhook, name="userfront_webhook")]
