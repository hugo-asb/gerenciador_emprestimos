from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
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

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class ListPaymentsByLoanViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if "loan_id" in self.kwargs:
            return Payment.objects.filter(loan=self.kwargs["loan_id"]).order_by("-date")

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
