from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from daily_expense.models import Expense

User=get_user_model()


#Serializer to Get CustomUser Details using Django Token Authentication
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","email","password"]

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

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validators(self, attrs):
        data = super(CustomTokenObtainPairSerializer,self).validate(attrs)
        user =UserSerializer(self.user)
        data.update({'user':user.data})
        return data

class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'expense_name', 'amount_spent','date_of_transaction', 'category']


class TotalExpenseSerializer(serializers.Serializer):
    total_expense = serializers.DecimalField(max_digits=20, decimal_places=2)




