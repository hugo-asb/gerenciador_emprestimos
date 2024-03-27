import datetime
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from loans.models import Loan
from loans.api.serializers import LoanSerializer


class LoanTests(APITestCase):
    TODAY = datetime.date.today()
    MATURITY_DATE = datetime.date(TODAY.year + 1, TODAY.month, TODAY.day)
    LOAN_PATCH_REQ_BODY = {"interest_rate": 2.50, "nominal_value": 12000.00}
    LOAN_POST_REQ_BODY = {
        "nominal_value": 100000.00,
        "interest_rate": 1.00,
        "bank": "Bank Test",
        "maturity_date": MATURITY_DATE,
    }
    PERMISSION_DENIED_ERROR_MSG = "Permission Denied"
    INVALID_INTEREST_RATE_ERROR_MSG = "Interest rate must be greater than zero"
    INVALID_NOMINAL_VALUE_ERROR_MSG = "Nominal value must be greater than zero"
    INVALID_MATURITY_DATE_ERROR_MSG = (
        "Loan maturity date must be greater than request date"
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
        self.login()

    def login(self):
        self.client.force_authenticate(self.test_user)

    # Tests for get loan endpoint
    def test_get_valid_loan(self):
        response = self.client.get(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, LoanSerializer(self.test_loan).data)

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
        self.assertEqual(
            str(response.data["detail"]),
            self.PERMISSION_DENIED_ERROR_MSG,
        )

    # Tests for patch loans
    def test_patch_valid_loan(self):
        response = self.client.patch(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk]),
            self.LOAN_PATCH_REQ_BODY,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Decimal(response.data["interest_rate"]),
            Decimal(self.LOAN_PATCH_REQ_BODY["interest_rate"]),
        )
        self.assertEqual(
            Decimal(response.data["nominal_value"]),
            Decimal(self.LOAN_PATCH_REQ_BODY["nominal_value"]),
        )

    def test_patch_loan_with_invalid_interest_rate(self):
        request_body = {"interest_rate": -2.50}
        response = self.client.patch(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk]), request_body
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["interest_rate"]["detail"]),
            self.INVALID_INTEREST_RATE_ERROR_MSG,
        )

    def test_patch_loan_with_invalid_nominal_value(self):
        request_body = {"nominal_value": 0}
        response = self.client.patch(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk]), request_body
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["nominal_value"]["detail"]),
            self.INVALID_NOMINAL_VALUE_ERROR_MSG,
        )

    def test_patch_inexistent_loan(self):
        response = self.client.patch(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk + 9999]),
            self.LOAN_PATCH_REQ_BODY,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_loan_without_a_token(self):
        self.client.logout()
        response = self.client.patch(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk]),
            self.LOAN_PATCH_REQ_BODY,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_loan_from_another_user(self):
        self.client.logout()
        self.client.force_authenticate(self.test_user2)
        response = self.client.patch(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk]),
            self.LOAN_PATCH_REQ_BODY,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(response.data["detail"]),
            self.PERMISSION_DENIED_ERROR_MSG,
        )

    # Tests for delete loans
    def test_delete_valid_loan(self):
        response = self.client.delete(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_inexistent_loan(self):
        response = self.client.delete(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk + 9999])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_loan_without_a_token(self):
        self.client.logout()
        response = self.client.delete(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_loan_from_another_user(self):
        self.client.logout()
        self.client.force_authenticate(self.test_user2)
        response = self.client.delete(
            reverse("loan_get_patch_delete", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(response.data["detail"]),
            self.PERMISSION_DENIED_ERROR_MSG,
        )

    # Tests for post loans
    def test_post_valid_loan(self):
        response = self.client.post(
            reverse("create_new_loan"),
            self.LOAN_POST_REQ_BODY,
        )
        posted_loan = Loan.objects.last()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, LoanSerializer(posted_loan).data)

    def test_post_loan_with_invalid_interest_rate(self):
        request_body = dict(self.LOAN_POST_REQ_BODY)
        request_body["interest_rate"] = -2.5
        response = self.client.post(
            reverse("create_new_loan"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["interest_rate"]["detail"]),
            self.INVALID_INTEREST_RATE_ERROR_MSG,
        )

    def test_post_loan_with_invalid_nominal_value(self):
        request_body = dict(self.LOAN_POST_REQ_BODY)
        request_body["nominal_value"] = 0
        response = self.client.post(
            reverse("create_new_loan"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["nominal_value"]["detail"]),
            self.INVALID_NOMINAL_VALUE_ERROR_MSG,
        )

    def test_post_loan_with_invalid_maturity_date(self):
        request_body = dict(self.LOAN_POST_REQ_BODY)
        request_body["maturity_date"] = datetime.date(
            self.TODAY.year - 1, self.TODAY.month, self.TODAY.day
        )
        response = self.client.post(
            reverse("create_new_loan"),
            request_body,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            str(response.data["maturity_date"]["detail"]),
            self.INVALID_MATURITY_DATE_ERROR_MSG,
        )

    def test_post_loan_without_a_token(self):
        self.client.logout()
        response = self.client.post(
            reverse("create_new_loan"),
            self.LOAN_POST_REQ_BODY,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for get loan outstanding balance
    def test_get_loan_outstanding_balance(self):
        serialized_test_loan = LoanSerializer(self.test_loan).data
        response = self.client.get(
            reverse("loan_get_outstanding_balance", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], serialized_test_loan["id"])
        self.assertEqual(response.data["user"], serialized_test_loan["user"])
        self.assertEqual(
            response.data["outstanding_balance"],
            serialized_test_loan["total_debt"] - serialized_test_loan["total_paid"],
        )

    def test_get_nonexistent_loan_outstanding_balance(self):
        response = self.client.get(
            reverse("loan_get_outstanding_balance", args=[self.test_loan.pk + 9999])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_loan_outstanding_balance_without_a_token(self):
        self.client.logout()
        response = self.client.get(
            reverse("loan_get_outstanding_balance", args=[self.test_loan.pk + 9999])
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_loan_outstanding_balance_from_another_user(self):
        self.client.logout()
        self.client.force_authenticate(self.test_user2)
        response = self.client.get(
            reverse("loan_get_outstanding_balance", args=[self.test_loan.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            str(response.data["detail"]),
            self.PERMISSION_DENIED_ERROR_MSG,
        )

    # Tests for get loan list
    def test_get_loan_list(self):
        response = self.client.get("/api/loans/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data["results"][0], LoanSerializer(self.test_loan).data
        )
        self.assertDictEqual(
            response.data["results"][1], LoanSerializer(self.test_loan2).data
        )
        self.assertGreater(len(response.data["results"]), 0)
        self.assertGreater(response.data["count"], 0)
        self.assertTrue("links" in response.data.keys())

    def test_get_loan_list_without_a_token(self):
        self.client.logout()
        response = self.client.get("/api/loans/list/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_loan_list_from_user_with_no_loans_returns_empty_list(self):
        self.client.logout()
        self.client.force_authenticate(self.test_user2)
        response = self.client.get("/api/loans/list/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], 0)
        self.assertTrue("links" in response.data.keys())
