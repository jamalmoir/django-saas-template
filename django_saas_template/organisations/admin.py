from django.contrib import admin
from organisations import models


@admin.register(models.Organisation)
class OrganisationsAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
