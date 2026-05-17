from datetime import date
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import Employee, Customer

User = get_user_model()


class EmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Ensures that inactive employee cannot log in.
    """

    def validate(self, attrs):
        
        data = super().validate(attrs)

        user = self.user

        if hasattr(user, "employee_profile"):

            if (
                user.employee_profile.employment_status
                != Employee.EmploymentStatus.ACTIVE
            ):
                raise AuthenticationFailed(
                    "Your employee account is inactive."
                )
            
        return data


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for customer registration. Creates a new Django authentication user and related customer profile.
    """
    password = serializers.CharField(write_only=True, min_length=5)

    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "date_of_birth",
            "password"
        ]
        extra_kwargs = {
            "first_name": {
                "help_text": "First name of the customer"
            },
            "last_name": {
                "help_text": "Last name of the customer"
            },
            "email": {
                "help_text": "Email of the customer"
            },
            "phone_number": {
                "help_text": "Phone number of the customer"
            },
            "address": {
                "help_text": "Address of the customer"
            },
            "date_of_birth": {
                "help_text": "Date of birth of the customer (YYYY-MM-DD)"
            },
            "password": {
                "help_text": "Password for the customer's account"
            }
        }
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        customer = Customer.objects.create(
            user=user,
            **validated_data
        )

        return customer
    
class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for employee registration. Creates a new Django authentication user and related employee profile.
    """
    password = serializers.CharField(write_only=True, min_length=5)

    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "hire_date",
            "salary",
            "password"
        ]
        extra_kwargs = {
            "first_name": {
                "help_text": "First name of the employee"
            },
            "last_name": {
                "help_text": "Last name of the employee"
            },
            "email": {
                "help_text": "Email of the employee"
            },
            "phone_number": {
                "help_text": "Phone number of the employee"
            },
            "role": {
                "help_text": "Role of the employee"
            },
            "hire_date": {
                "help_text": "Hire date of the employee"
            },
            "salary": {
                "help_text": "Monthly salary of the employee"
            },
            "password": {
                "help_text": "Password for the employee's account"
            }
        }
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        employee = Employee.objects.create(
            user=user,
            **validated_data
        )

        return employee
    
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=5)

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "hire_date",
            "salary",
            "created_at",
            "employment_status",
            "layoff_date"
        ]
        read_only_fields = [
            "id",
            "created_at"
        ]

class EmployeeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "hire_date",
            "salary",
            "created_at",
        ]
        read_only_fields = fields

class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "date_of_birth",
            "created_at"
        ]
        read_only_fields = [
            "id",
            "email",
            "created_at",
            "date_of_birth"
        ]

class AdminEmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "hire_date",
            "salary",
            "created_at"
        ]
        read_only_fields = [
            "id",
            "created_at",
            "email",
        ]

class AdminEmployeeEmploymentStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Allow admin employees to update only the employment status and layoff date of an employee.
    """
    class Meta:
        model = Employee
        fields = [
            "id",
            "employment_status",
            "layoff_date"
        ]
        extra_kwargs = {
            "employment_status": {
                "help_text": "Employment status of the employee (active or inactive)"
            },
            "layoff_date": {
                "help_text": "Layoff date of the employee (YYYY-MM-DD)"
            }
        }
        read_only_fields = ["id"]