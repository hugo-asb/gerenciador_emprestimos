from decimal import Decimal
from django.db import models
from django.db.models import Sum
from payments.models import Payment


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

    def calculate_iof(self):
        iof_tax = Decimal(0.38 / 100)
        daily_amortization = Decimal(0.0082 / 100)
        total_days = (self.maturity_date - self.request_date).days
        tax = self.nominal_value * iof_tax
        amortization = self.nominal_value * total_days * daily_amortization
        return round(tax + amortization, 2)

    @property
    def get_total_interest(self):
        iof_tax = self.calculate_iof()
        initial_value = self.nominal_value
        interest_rate = self.interest_rate / 100
        period = self.get_total_installments
        total_debt = initial_value * ((1 + interest_rate) ** period)
        total_interest = total_debt - initial_value
        return round(total_interest + iof_tax, 2)

    @property
    def get_total_paid(self):
        total_paid = Payment.objects.filter(loan=self.id).aggregate(Sum("value"))
        if total_paid["value__sum"]:
            return total_paid["value__sum"]
        return 0

    @property
    def get_balance(self):
        total_debt = self.nominal_value + self.get_total_interest
        return total_debt - self.get_total_paid

    @property
    def get_total_debt(self):
        return self.nominal_value + self.get_total_interest
