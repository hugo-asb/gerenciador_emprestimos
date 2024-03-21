from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from loans.models import Loan
from loans.api.serializers import LoanSerializer
from loans.paginations import CustomPagination


class LoanViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = LoanSerializer

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user).order_by("-request_date")

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
