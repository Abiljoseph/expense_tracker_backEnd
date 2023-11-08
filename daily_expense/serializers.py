from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from daily_expense.models import Expense

User=get_user_model()


#Serializer to Register CustomUser
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,
                                   validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,required=True,validators=[validate_password])

    class Meta:
        model = User
        fields = ('username','email','password')


    def create(self,validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email = validated_data['email']

        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['expense_name', 'amount_spent','date_of_transaction', 'category']

class CurrentMonthExpenseSerializer(serializers.Serializer):
    total_expense = serializers.DecimalField(max_digits=10, decimal_places=2)

class TotalAmountbyCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=50, decimal_places=2)

class YearlyReportSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    monthly_expenses = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )

class MonthReportSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    daily_expenses = serializers.DictField(
        child=serializers.DecimalField(max_digits=10, decimal_places=2)
    )





