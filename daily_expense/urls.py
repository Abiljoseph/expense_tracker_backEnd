from django.urls import path
from .views import RegistrationView, CreateExpenseView, ListExpenseView, PasswordResetView, \
    TotalExpenseCurrentMonth, RecentTransactions, EditExpense

app_name ='daily_expense'

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('passwordreset/',PasswordResetView.as_view(), name='passwordreset'),
    path('create/', CreateExpenseView.as_view(), name='create'),
    path('list/', ListExpenseView.as_view(), name='list'),
    path('total_expense_current_month/', TotalExpenseCurrentMonth.as_view(),
         name='total_expense_current_month'),
    path('recent_transactions/', RecentTransactions.as_view(), name='recent_transactions'),
    path('edit_expense/<int:expense_id>/', EditExpense.as_view(), name='edit_expense'),
]
