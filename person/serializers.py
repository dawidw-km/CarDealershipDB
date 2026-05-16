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
        read_only_fields = [
            "id",
            "email",
            "created_at",

        ]

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
        read_only_fields = ["id"]