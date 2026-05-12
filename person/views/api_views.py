from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from ..models import Customer, Employee
from ..serializers import (
    CustomerSerializer,
    EmployeeSerializer,
    CustomerRegistrationSerializer,
    EmployeeRegistrationSerializer,
    CustomerDetailSerializer,
)
from ..permissions import IsEmployeeAdmin, IsAnonymous

# API Views
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


class CustomerRegistrationView(generics.CreateAPIView):
    """
    Allow anonymous users to create customer accounts.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [IsAnonymous]


class CustomerDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update the authenticated customer's profile.
    """
    serializer_class = CustomerDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.customer_profile


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Allow employee admins to manage employee profiles.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployeeAdmin]


class EmployeeRegistrationView(generics.CreateAPIView):
    """
    Allow employee admins to create employee accounts.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeRegistrationSerializer
    permission_classes = [IsEmployeeAdmin]


class EmployeeListView(generics.ListAPIView):
    """
    Allow employee admins to list all employee profiles.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployeeAdmin]