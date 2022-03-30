from django.contrib import admin
from django_saas_template.subscriptions import models


@admin.register(models.SaasPlan)
class SaasPlansAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
