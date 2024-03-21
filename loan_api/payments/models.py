from django.db import models


class Payment(models.Model):
    loan = models.ForeignKey("loans.Loan", on_delete=models.CASCADE)
    date = models.DateField()
    value = models.DecimalField(decimal_places=2, max_digits=12)
