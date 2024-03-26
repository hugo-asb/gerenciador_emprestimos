from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from payments.models import Payment
from loans.models import Loan
from payments.api.serializers import PaymentSerializer
from loan_api.paginations import CustomPagination


class ListAllPaymentsViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = PaymentSerializer

    def get_queryset(self):
        loans_id = Loan.objects.filter(user=self.request.user).values_list(
            "id", flat=True
        )
        return Payment.objects.filter(loan__in=loans_id).order_by("-date")


class ListPaymentsByLoanViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if "loan_id" in self.kwargs:
            loan_id = self.kwargs["loan_id"]
            loan = get_object_or_404(Loan, pk=loan_id)
            if self.request.user != loan.user:
                raise PermissionDenied("Permission Denied")
            return Payment.objects.filter(loan=loan_id).order_by("-date")
