from django.urls import path
from .views import RegistrationView, CreateExpenseView, ExpenseListView, PasswordResetView, \
    RecentTransactions, EditExpense, PastExpenseListView, CurrentMonthExpenseView, MonthExpenseReportsView, \
    YearlyExpenseReportsView, TotalAmountByCategoryView

app_name ='daily_expense'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('passwordreset/',PasswordResetView.as_view(), name='passwordreset'),
    path('create/', CreateExpenseView.as_view(), name='create'),
    path('list/', ExpenseListView.as_view(), name='list'),
    path('totalexpense/', CurrentMonthExpenseView.as_view(),
         name='totalexpense'),
    path('recent_transactions/', RecentTransactions.as_view(), name='recent_transactions'),
    path('edit_expense/<int:expense_id>/', EditExpense.as_view(), name='edit_expense'),
    path('pastexpense/',PastExpenseListView.as_view(),name='pastexpense'),
    path('total-amount-by-category/',TotalAmountByCategoryView.as_view(),name='total-amount-by-category'),
    path('yearly-report/', YearlyExpenseReportsView.as_view(),name='yearly-report'),
    path('monthly-report/',MonthExpenseReportsView.as_view(),name='monthly-report'),
]
