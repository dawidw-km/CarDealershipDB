from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from .models import Customer, Employee
from .serializers import CustomerSerializer, EmployeeSerializer, CustomerRegistrationSerializer, EmployeeRegistrationSerializer
from .permissions import IsEmployeeAdmin, IsAnonymous

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployeeAdmin]
    
class CustomerRegistrationView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [IsAnonymous]

class EmployeeRegistrationView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeRegistrationSerializer
    permission_classes = [IsEmployeeAdmin]

class EmployeeListView(generics.ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployeeAdmin]