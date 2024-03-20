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
    bank = models.CharField(max_length=100)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
