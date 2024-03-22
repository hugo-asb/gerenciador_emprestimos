import datetime
from django.db import models


class Loan(models.Model):
    nominal_value = models.DecimalField(
        verbose_name="Nominal value", decimal_places=2, max_digits=12
    )
    interest_rate = models.DecimalField(
        verbose_name="interest_rate", decimal_places=2, max_digits=12
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP address")
    request_date = models.DateField(auto_now_add=True)
    maturity_date = models.DateField(blank=False)
    bank = models.CharField(max_length=100)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    @property
    def get_total_installments(self):
        request_date = self.request_date
        maturity_date = self.maturity_date
        total_installments = (maturity_date.month - request_date.month) + (
            ((maturity_date.year - request_date.year) * 12)
        )
        return total_installments
