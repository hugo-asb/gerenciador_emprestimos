from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from loans.models import Loan
from payments.api.serializers import PaymentSerializer
from payments.models import Payment


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def retrieve_valid_payment(self, request, payment_id):
        payment = get_object_or_404(Payment, pk=payment_id)
        if request.user != payment.loan.user:
            raise PermissionDenied("Permission Denied")
        return payment

    def get(self, request, id):
        payment = self.retrieve_valid_payment(request=request, payment_id=id)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def delete(self, request, id):
        payment = self.retrieve_valid_payment(request=request, payment_id=id)
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentPost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        loan = get_object_or_404(Loan, pk=request.data["loan"])

        if loan.user != request.user:
            raise PermissionDenied("This loan is not bonded with you")

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
