from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Expense

admin.site.register(CustomUser)
admin.site.register(Expense)