from django.contrib import admin
from . import models


class LoanAdmin(admin.ModelAdmin):
    search_fields = ("user",)
    list_display = (
        "id",
        "user",
        "bank",
        "ip_address",
        "nominal_value",
        "interest_rate",
        "request_date",
        "maturity_date",
    )


admin.site.register(models.Loan, LoanAdmin)
