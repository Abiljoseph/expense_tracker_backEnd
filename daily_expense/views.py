from django.db.models import Sum
from django.utils.datetime_safe import date
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Expense
from .serializers import UserSerializer, RegisterSerializer, ExpenseSerializer, PasswordResetSerializer, \
    TotalExpenseSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash


# Class based view to register user
class RegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


# Class based view to Get CustomUser Details using Token Authentication
class LoginView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, args, *kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class PasswordResetView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if request.method == 'POST':
            serializer = PasswordResetSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                if user.check_password(serializer.data.get('old_password')):
                    user.set_password(serializer.data.get('new_password'))
                    user.save()
                    update_session_auth_hash(request, user)  # To update session after password change
                    return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
                return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateExpenseView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class ListExpenseView(generics.ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class TotalExpenseCurrentMonth(APIView):
    def get(self, request):
        current_month = date.today().month
        total_expense = Expense.objects.filter(date_of_transaction__month=current_month).aggregate(Sum('amount_spent'))[
            'amount_spent__sum']

        serializer = TotalExpenseSerializer({'total_expense': total_expense})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecentTransactions(APIView):
    def get(self, request):
        recent_transactions = Expense.objects.all().order_by('-date_of_transaction')[:10]
        # Get the 10 most recent transactions
        serializer = ExpenseSerializer(recent_transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditExpense(APIView):
    serializer_class = ExpenseSerializer

    def get(self, request, expense_id):
        try:
            expense = Expense.objects.get(id=expense_id)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, expense_id):
        try:
            expense = Expense.objects.get(id=expense_id)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, expense_id):
        try:
            expense = Expense.objects.get(id=expense_id)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)

        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
