import calendar
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Expense
from .pagination import StandardResultsSetPagination
from .serializers import RegisterSerializer, ExpenseSerializer, PasswordResetSerializer, \
    CurrentMonthExpenseSerializer, MonthReportSerializer, YearlyReportSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash


# Class based view to register user
class RegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class CreateExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Expense.objects.filter(user=request.user)
        serializer = ExpenseSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response({'message': 'Expense added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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


class CreateExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Expense.objects.filter(user=request.user)
        serializer = ExpenseSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            return Response({'message': 'Expense added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentMonthExpenseView(APIView):
    serializer_class = CurrentMonthExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        current_month = datetime.now().month
        current_year = datetime.now().year

        expense = Expense.objects.filter(
            user=user,
            date_of_transaction__gte=datetime(current_year, current_month, 1),
            date_of_transaction__lt=datetime(current_year, current_month + 1, 1)
        )
        total_expense=0
        for i in expense:

            total_expense += Decimal(str(i.amount_spent))

        serializer = CurrentMonthExpenseSerializer({'total_expense': total_expense})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecentTransactions(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user=self.request.user
        recent_transactions = Expense.objects.filter(user=user).order_by('-date_of_transaction')[:10]
        # Get the 10 most recent transactions
        serializer = ExpenseSerializer(recent_transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EditExpense(APIView):
    permission_classes = [IsAuthenticated]
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


class PastExpenseListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all().order_by('-date_of_transaction')
    serializer_class = ExpenseSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user=self.request.user
        return Expense.objects.filter(user=user)


class ExpenseListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        queryset = Expense.objects.filter(user=self.request.user)
        category = self.request.query_params.get('category')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        search_term = self.request.query_params.get('search')

        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                end_date+=timedelta(days=1)
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            queryset = queryset.filter(
                Q(date_of_transaction__gte=start_date) &
                Q(date_of_transaction__lte=end_date)
            )

        if category:
            queryset = queryset.filter(category=category)

        if search_term:
            queryset = queryset.filter(expense_name__icontains=search_term)

        serializer = ExpenseSerializer(queryset, many=True)
        return Response(serializer.data)


class YearlyExpenseReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = self.request.user
        selected_year = self.request.query_params.get('year')  # Get the selected year from the request

        # Check if the selected year is valid (you may want to add further validation)
        if not selected_year:
            return Response({'error': 'Year not specified'}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize a dictionary to store expenses for each month
        monthly_expenses = {
            1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0
        }

        # Get all expenses for the selected year
        expenses = Expense.objects.filter(
            user=user).filter(
            date_of_transaction__year=selected_year)


        # Calculate monthly expenses
        for expense in expenses:
            print(expense)
            month = expense.date_of_transaction.month
            amount_spent = expense.amount_spent

            monthly_expenses[month] +=Decimal(str(amount_spent))

        # Serialize the report data
        report_data = {
            'year': selected_year,
            'monthly_expenses': monthly_expenses
        }

        serializer = YearlyReportSerializer(report_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MonthExpenseReportsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = self.request.user
        selected_year = self.request.query_params.get('year')  # Get the selected year from the request
        selected_month = self.request.query_params.get('month')  # Get the selected month from the request

        # Check if the selected year and month are valid (you may want to add further validation)
        if not selected_year or not selected_month:
            return Response({'error': 'Year and month not specified'}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the selected year and month as integers
        selected_year = int(selected_year)
        selected_month = int(selected_month)

        # Calculate the number of days in the selected month
        days_in_month = calendar.monthrange(selected_year, selected_month)[1]

        # Initialize a dictionary to store expenses for each day
        daily_expenses = {}

        # Get all expenses for the selected month and year
        expenses = Expense.objects.filter(
            user=user).filter(
            date_of_transaction__gte=datetime(selected_year, selected_month, 1),
            date_of_transaction__lt=datetime(selected_year, selected_month + 1, 1)
        )

        # Calculate daily expenses
        for day in range(1, days_in_month + 1):
            daily_expenses[day] = 0

        for expense in expenses:
            day = expense.date_of_transaction.day
            amount_spent = expense.amount_spent

            # Accumulate daily expenses
            daily_expenses[day] += Decimal(str(amount_spent))

        # Serialize the report data
        report_data = {
            'year': selected_year,
            'month': selected_month,
            'daily_expenses': daily_expenses
        }

        serializer = MonthReportSerializer(report_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TotalAmountByCategoryView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request):
        user = self.request.user
        categories = Expense.objects.filter(user=user)
        total_expenses = {}

        for i in categories:
            if i.category in total_expenses:
                total_expenses[i.category] += Decimal(str(i.amount_spent))
            else:
                total_expenses[i.category]=Decimal(str(i.amount_spent))

        return Response(total_expenses)