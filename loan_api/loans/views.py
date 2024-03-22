from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from loans.api.serializers import LoanSerializer
from loans.models import Loan


class LoanView(APIView):
    permission_classes = [IsAuthenticated]

    def retrieve_valid_loan(self, request, loan_id):
        loan = get_object_or_404(Loan, pk=loan_id)
        if request.user != loan.user:
            raise PermissionDenied("Permission Denied")
        return loan

    def get(self, request, id):
        loan = self.retrieve_valid_loan(request=request, loan_id=id)
        serializer = LoanSerializer(loan, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, id):
        loan = self.retrieve_valid_loan(request=request, loan_id=id)
        serializer = LoanSerializer(loan, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        loan = self.retrieve_valid_loan(request=request, loan_id=id)
        loan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoanPost(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LoanSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
