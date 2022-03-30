from django.contrib import admin
from django_saas_template.organisations import models


@admin.register(models.Organisation)
class OrganisationsAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
