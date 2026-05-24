from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from ..models import Customer, Employee
from ..serializers import (
    EmployeeSerializer,
    EmployeeDetailSerializer,
    PasswordChangeSerializer,
    CustomerRegistrationSerializer,
    EmployeeRegistrationSerializer,
    CustomerDetailSerializer,
    AdminEmployeeUpdateSerializer,
    AdminEmployeeEmploymentStatusUpdateSerializer,
    EmployeeTokenObtainPairSerializer,
    CustomerTokenObtainPairSerializer
)
from ..permissions import IsEmployeeAdmin, IsAnonymous, IsCustomer, IsEmployeeActive
from rest_framework_simplejwt.views import TokenObtainPairView

@extend_schema(tags=["Authentication"])
class EmployeeLoginView(TokenObtainPairView):
    """
    Return JWT tokens only if user is allowed to sign in.
    """
    serializer_class = EmployeeTokenObtainPairSerializer

@extend_schema(tags=["Authentication"])
class CustomerLoginView(TokenObtainPairView):
    """
    Return JWT tokens only if user is allowed to sign in.
    """
    serializer_class = CustomerTokenObtainPairSerializer

@extend_schema(
    tags=["Customers"],
    examples=[
        OpenApiExample(
            name="Customer registration",
            value={
                "first_name": "John",
                "last_name": "Snow",
                "email": "customer@example.com",
                "phone_number": "+48123456789",
                "address": "Warszawa 12",
                "date_of_birth": "1990-01-01",
                "password": "StrongPassword123"
            }
        )
    ]
)
class CustomerRegistrationView(generics.CreateAPIView):   
    """
    Allow anonymous users to create customer accounts.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [IsAnonymous]


@extend_schema(tags=["Customers"])
class CustomerDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update the authenticated customer's profile.
    """
    serializer_class = CustomerDetailSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_object(self):
        return self.request.user.customer_profile

@extend_schema(tags=["Authentication"])
class ChangePasswordView(generics.UpdateAPIView):
    """
    Allow authenticated users to change their password.
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
           return Response({"old_password": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
        
        if (old_password == new_password):
            return Response(
                {"new_password": "New password cannot be the same as the old password."},
                  status=status.HTTP_400_BAD_REQUEST
                )

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
    
 
@extend_schema(
    tags=["Employees"],
    examples=[
        OpenApiExample(
            name="Employee registration",
            value={
                "first_name": "John",
                "last_name": "Snow",
                "email": "employee@example.com",
                "phone_number": "+48123456789",
                "role": "worker",
                "hire_date": "2026-05-17",
                "salary": "10000.00",
                "password": "StrongPassword123"
            },
            request_only=True,
        )
    ]
)
class EmployeeRegistrationView(generics.CreateAPIView):
    """
    Allow employee admins to create employee accounts.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeRegistrationSerializer
    permission_classes = [IsAuthenticated, IsEmployeeAdmin]


@extend_schema(tags=["Employees"])
class EmployeeDetailView(generics.RetrieveAPIView):
    """
    Allow employee admins to retrieve employee profiles.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeDetailSerializer
    permission_classes = [IsEmployeeActive, IsAuthenticated]

    def get_object(self):
        return self.request.user.employee_profile

@extend_schema(tags=["Employees"])
class EmployeeListView(generics.ListAPIView):
    """
    Allow employee admins to list all employee profiles.
    """
    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployeeAdmin, IsAuthenticated]


@extend_schema(tags=["Employees"])
class AdminEmployeeUpdateView(generics.UpdateAPIView):
    """
    Allow employee admins to update employee profiles.
    """
    queryset = Employee.objects.all()
    serializer_class = AdminEmployeeUpdateSerializer
    permission_classes = [IsEmployeeAdmin, IsAuthenticated]


@extend_schema(tags=["Employees"])
class AdminEmployeeEmploymentStatusUpdateView(generics.UpdateAPIView):
    """
    Allow employee admins to update employee employment status.
    """
    queryset = Employee.objects.all()
    serializer_class = AdminEmployeeEmploymentStatusUpdateSerializer
    permission_classes = [IsEmployeeAdmin, IsAuthenticated]
