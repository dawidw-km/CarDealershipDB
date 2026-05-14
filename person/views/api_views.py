from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from ..models import Customer, Employee
from ..serializers import (
    EmployeeSerializer,
    PasswordChangeSerializer,
    CustomerRegistrationSerializer,
    EmployeeRegistrationSerializer,
    CustomerDetailSerializer,
)
from ..permissions import IsEmployeeAdmin, IsAnonymous

@extend_schema(tags=["Customers"])
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
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.customer_profile

class ChangePasswordView(generics.UpdateAPIView):
    """
    Allow authenticated users to change their password.
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def update_password(self, request, *args, **kwargs):

        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": "Wrong password."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        



@extend_schema(tags=["Employees"])
class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Allow employee admins to manage employee profiles.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployeeAdmin]

@extend_schema(tags=["Employees"])
class EmployeeRegistrationView(generics.CreateAPIView):
    """
    Allow employee admins to create employee accounts.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeRegistrationSerializer
    permission_classes = [IsEmployeeAdmin]

@extend_schema(tags=["Employees"])
class EmployeeListView(generics.ListAPIView):
    """
    Allow employee admins to list all employee profiles.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployeeAdmin]