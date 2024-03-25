from django.contrib import admin
from . import models


class PaymentAdmin(admin.ModelAdmin):
    search_fields = ("loan",)
    list_display = (
        "id",
        "loan",
        "date",
        "value",
    )


admin.site.register(models.Payment, PaymentAdmin)
