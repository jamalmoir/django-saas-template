from django.contrib import admin
from django_saas_template.users import models


@admin.register(models.SaasUser)
class SaasUsersAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
