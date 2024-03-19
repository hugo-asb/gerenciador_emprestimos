from django.contrib import admin
from . import models


class UserAdmin(admin.ModelAdmin):
    search_fields = ("email",)
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_superuser",
    )


admin.site.register(models.User, UserAdmin)
