import datetime
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from loans.models import Loan
from payments.models import Payment
from payments.api.serializers import PaymentSerializer


class PaymentTests(APITestCase):
    TODAY = datetime.date.today()
    MATURITY_DATE = datetime.date(TODAY.year + 1, TODAY.month, TODAY.day)
    PERMISSION_DENIED_ERROR_MSG = "Permission Denied"
    INVALID_PAYMENT_VALUE_ERROR_MSG = "Payment value must be greater than zero"
    DATE_BEFORE_LOAN_REQUEST_DATE_ERROR_MSG = (
        "Only payments past loan request date are acceptable"
    )
    DATE_PAST_LOAN_MATURITY_DATE_ERROR_MSG = (
        "Payments past loan maturity date are not acceptable"
    )
    PAYMENT_BIGGER_THAN_TOTAL_DEBT_ERROR_MSG = (
        "Payments can not be bigger than total debt"
    )
    TOTAL_PAYMENTS_EXCEEDS_TOTAL_DEBT_ERROR_MSG = (
        "Total payments exceed total debt value"
    )

    def setUp(self):
        self.test_user = User.objects.create(
            username="test-user",
            email="test-user@test.com",
            password="test-password",
        )
        self.test_user2 = User.objects.create(
            username="test-user2",
            email="test-user2@test.com",
            password="test-password2",
        )
        self.test_loan = Loan.objects.create(
            user=self.test_user,
            nominal_value=Decimal(100000.00),
            ip_address="0.0.0.0",
            interest_rate=Decimal(1.8),
            bank="Bank Test",
            maturity_date=self.MATURITY_DATE,
        )
        self.test_loan2 = Loan.objects.create(
            user=self.test_user,
            nominal_value=Decimal(50000.00),
            ip_address="0.0.0.0",
            interest_rate=Decimal(3.6),
            bank="Bank Test",
            maturity_date=self.MATURITY_DATE,
        )
        self.test_loan_user2 = Loan.objects.create(
            user=self.test_user2,
            nominal_value=Decimal(50000.00),
            ip_address="0.0.0.0",
            interest_rate=Decimal(2.35),
            bank="Bank Test",
            maturity_date=self.MATURITY_DATE,
        )
        self.test_payment = Payment.objects.create(
            loan=self.test_loan,
            date=self.generate_date(months_to_add=1),
            value=Decimal(1000.00),
        )
        self.test_payment = Payment.objects.create(
            loan=self.test_loan,
            date=self.generate_date(months_to_add=2),
            value=Decimal(2000.00),
        )
        self.login()

    def login(self):
        self.client.force_authenticate(self.test_user)

    def generate_date(self, months_to_add):
        total_months = self.TODAY.month + months_to_add
        if total_months > 12:
            years_to_add = total_months % 12
            months_to_add = int(total_months / 12)
            return datetime.date(
                self.TODAY.year + years_to_add, months_to_add, self.TODAY.day
            )
        return datetime.date(
            self.TODAY.year, self.TODAY.month + months_to_add, self.TODAY.day
        )

    # Tests for get payment
    def test_get_valid_payment(self):
        response = self.client.get(
            reverse("payment_methods", args=[self.test_payment.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, PaymentSerializer(self.test_payment).data)

    def test_get_nonexistent_payment(self):
        response = self.client.get(
            reverse("payment_methods", args=[self.test_payment.pk + 9999])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_payment_without_a_token(self):
        self.client.logout()
        response = self.client.get(
            reverse("payment_methods", args=[self.test_payment.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_payment_from_another_user(self):
        self.client.logout()
        self.client.force_authenticate(self.test_user2)
        response = self.client.get(
            reverse("payment_methods", args=[self.test_payment.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaisesMessage(response.data, self.PERMISSION_DENIED_ERROR_MSG)

    # Tests for delete payment
    def test_delete_valid_payment(self):
        response = self.client.delete(
            reverse("payment_methods", args=[self.test_payment.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_inexistent_payment(self):
        response = self.client.get(
            reverse("payment_methods", args=[self.test_payment.pk + 9999])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_payment_without_a_token(self):
        self.client.logout()
        response = self.client.get(
            reverse("payment_methods", args=[self.test_payment.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_payment_from_another_user(self):
        self.client.logout()
        self.client.force_authenticate(self.test_user2)
        response = self.client.get(
            reverse("payment_methods", args=[self.test_payment.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertRaisesMessage(response.data, self.PERMISSION_DENIED_ERROR_MSG)

    # Tests for post payments
    def test_post_valid_payment(self):
        request_body = {
            "loan": self.test_loan.id,
            "value": self.test_loan.nominal_value / 10,
            "date": self.generate_date(months_to_add=1),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        posted_payment = Payment.objects.last()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, PaymentSerializer(posted_payment).data)

    def test_post_payment_with_invalid_value(self):
        request_body = {
            "loan": self.test_loan.id,
            "value": 0,
            "date": self.generate_date(months_to_add=1),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["value"]["detail"]),
            self.INVALID_PAYMENT_VALUE_ERROR_MSG,
        )

    def test_post_payment_with_date_before_loan_request_date(self):
        loan_request_date = self.test_loan.request_date
        request_body = {
            "loan": self.test_loan.id,
            "value": self.test_loan.nominal_value / 10,
            "date": datetime.date(
                loan_request_date.year - 1,
                loan_request_date.month,
                loan_request_date.day,
            ),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["detail"][0]),
            self.DATE_BEFORE_LOAN_REQUEST_DATE_ERROR_MSG,
        )

    def test_post_payment_with_date_after_loan_maturity_date(self):
        loan_maturity_date = self.test_loan.maturity_date
        request_body = {
            "loan": self.test_loan.id,
            "value": self.test_loan.nominal_value / 10,
            "date": datetime.date(
                loan_maturity_date.year + 1,
                loan_maturity_date.month,
                loan_maturity_date.day,
            ),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["detail"][0]),
            self.DATE_PAST_LOAN_MATURITY_DATE_ERROR_MSG,
        )

    def test_post_payment_bigger_than_total_debt(self):
        request_body = {
            "loan": self.test_loan.id,
            "value": self.test_loan.get_total_debt * 2,
            "date": self.generate_date(months_to_add=1),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["detail"][0]),
            self.PAYMENT_BIGGER_THAN_TOTAL_DEBT_ERROR_MSG,
        )

    def test_post_payment_that_added_to_total_paid_exceeds_outstanding_balance(self):
        payment_value = (
            self.test_loan.get_balance
            - self.test_payment.value
            + (self.test_payment.value / 2)
        )
        request_body = {
            "loan": self.test_loan.id,
            "value": payment_value,
            "date": self.generate_date(months_to_add=1),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["detail"][0]),
            self.TOTAL_PAYMENTS_EXCEEDS_TOTAL_DEBT_ERROR_MSG,
        )

    def test_post_payment_without_a_token(self):
        self.client.logout()
        request_body = {
            "loan": self.test_loan.id,
            "value": self.test_loan.nominal_value / 10,
            "date": self.generate_date(months_to_add=1),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_payment_in_another_user_loan(self):
        request_body = {
            "loan": self.test_loan_user2.id,
            "value": self.test_loan.nominal_value / 10,
            "date": self.generate_date(months_to_add=1),
        }
        response = self.client.post(
            reverse("post_payment"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
