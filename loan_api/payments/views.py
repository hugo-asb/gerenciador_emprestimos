from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from loans.models import Loan
from payments.api.serializers import PaymentSerializer
from payments.models import Payment


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        payment = get_object_or_404(Payment, pk=id)
        if request.user != payment.loan.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def patch(self, request, id):
        payment = get_object_or_404(pk=id)
        if request.user != payment.loan.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        payment = get_object_or_404(pk=id)
        if request.user != payment.loan.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentPost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        loan_403_response = Response(
            {"detail": "This loan is not bonded with you"},
            status=status.HTTP_403_FORBIDDEN,
        )

        try:
            loan = Loan.objects.get(pk=request.data["loan"])
        except Loan.DoesNotExist:
            return loan_403_response

        if loan.user != request.user:
            return loan_403_response

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
