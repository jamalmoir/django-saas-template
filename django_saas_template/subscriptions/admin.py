from django.contrib import admin
from subscriptions import models


@admin.register(models.SaasPlan)
class SaasPlansAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
