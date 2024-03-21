from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from loans.models import Loan
from payments.api.serializers import PaymentSerializer
from payments.models import Payment


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_payment_by_id(self, id):
        try:
            payment = Payment.objects.get(pk=id)
            return payment
        except Payment.DoesNotExist:
            raise Http404

    def get(self, request, id):
        payment = self.get_payment_by_id(id)
        serializer = PaymentSerializer(payment)

        return Response(serializer.data)

    def patch(self, request, id):
        payment = self.get_payment_by_id(id)

        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        payment = self.get_payment_by_id(id)
        payment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentPost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        loan = Loan.objects.get(pk=request.data["loan"])
        if loan.user != request.user:
            return Response(
                {"detail": "This loan is not bonded with you"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
