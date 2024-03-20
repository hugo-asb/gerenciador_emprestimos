from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from loans.api.serializers import LoanSerializer
from loans.models import Loan


class LoanView(APIView):
    permission_classes = [IsAuthenticated]

    def get_loan_by_id(self, id):
        try:
            loan = Loan.objects.get(pk=id)
            return loan
        except Loan.DoesNotExist:
            raise Http404

    def get(self, request, id):
        loan = self.get_loan_by_id(id)
        serializer = LoanSerializer(loan, context={"request": request})

        return Response(serializer.data)

    def patch(self, request, id):
        loan = self.get_loan_by_id(id)

        serializer = LoanSerializer(loan, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        loan = self.get_loan_by_id(id)
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


class LoanList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        loans = Loan.objects.filter(user=request.user)
        serializer = LoanSerializer(loans, many=True)

        return Response(serializer.data)
