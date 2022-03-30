from django.contrib import admin
from users import models


@admin.register(models.SaasUser)
class SaasUsersAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
