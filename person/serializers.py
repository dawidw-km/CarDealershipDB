from datetime import date
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password as django_validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from .models import Employee, Customer

User = get_user_model()

def validate_unique_email(email):
    """
    Ensures that the email is not already in use.
    """
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Email already in use.")
    return email

class EmployeeTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Ensures that inactive employee cannot log in.
    """

    def validate(self, attrs):
        
        data = super().validate(attrs)
        user = self.user

        if not hasattr(user, "employee_profile"):
            raise AuthenticationFailed(
                "You must be an employee to sign in."
            )

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


    def validate_email(self, email):
       validate_unique_email(email)
       return email

    def validate_password(self, password):
            django_validate_password(password)
            return password

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new customer account and related customer profile.
        """

        password = validated_data.pop('password')
        email = validated_data.get('email')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        customer = Customer(
            user=user,
            **validated_data
        )
        try:
            customer.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        customer.save()

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


    def validate_email(self, email):
       validate_unique_email(email)
       return email

    def validate_password(self, password):
        django_validate_password(password)
        return password

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new employee account and related employee profile.
        """
        password = validated_data.pop('password')
        email = validated_data.get('email')


        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        employee = Employee(
            user=user,
            **validated_data
        )
        try:
            employee.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        employee.save()

        return employee
    
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=5)

    def validate_new_password(self, new_password):
        django_validate_password(new_password)
        return new_password

    def validate(self, attrs):
        """
        Ensures that the old password is correct.
        """
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        user = self.context['request'].user

        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {"old_password": "Old password is incorrect."}
                )

        if old_password == new_password:
            raise serializers.ValidationError(
                {"new_password": "New password cannot be the same as the old password."}
                )

        return attrs


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

    def update(self, instance, validated_data):
        """
        Update a customer profile and ensure that the user does not have an employee profile.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance

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

    def update(self, instance, validated_data):
        """
        Update an employee profile and ensure that the user does not have a customer profile.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.role = validated_data.get('role', instance.role)
        instance.hire_date = validated_data.get('hire_date', instance.hire_date)
        instance.salary = validated_data.get('salary', instance.salary)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance

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

    def update(self, instance, validated_data):
        """
        Update employment status fields and run model validation before saving.
        """
        instance.employment_status = validated_data.get('employment_status', instance.employment_status)
        instance.layoff_date = validated_data.get('layoff_date', instance.layoff_date)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        instance.save()
        return instance