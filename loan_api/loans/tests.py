import datetime
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from loans.models import Loan
from loans.api.serializers import LoanSerializer


class LoanTests(APITestCase):
    def setUp(self):
        today = datetime.date.today()
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
            maturity_date=datetime.date(today.year + 1, today.month, today.day),
        )
        self.test_loan2 = Loan.objects.create(
            user=self.test_user,
            nominal_value=Decimal(50000.00),
            ip_address="0.0.0.0",
            interest_rate=Decimal(3.6),
            bank="Bank Test",
            maturity_date=datetime.date(today.year + 1, today.month, today.day),
        )
        self.login()

    def login(self):
        self.client.force_authenticate(self.test_user)

    # Tests for get loan endpoint
    def test_get_valid_loan(self):
        response = self.client.get(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, LoanSerializer(self.test_loan).data)

    def test_get_nonexistent_loan(self):
        response = self.client.get(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk + 999999])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_loan_without_a_token(self):
        self.client.logout()
        response = self.client.get(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_loan_from_another_user(self):
        self.client.logout()
        self.client.force_authenticate(self.test_user2)
        response = self.client.get(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
