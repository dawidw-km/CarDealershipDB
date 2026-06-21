from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from sales.models import Sale
from sales.serializers import SaleRegistrationSerializer, SaleDetailSerializer
from person.permissions import IsCustomer, IsEmployeeActive
from cars.permissions import CannotBeCarOwner
from drf_spectacular.utils import extend_schema
from cars.models import Car

@extend_schema(tags=["Sales - Authenticated-Customer"])
class SaleRegistrationView(generics.CreateAPIView):
    """
    Allow authenticated customers to register a new sale.
    """
    queryset = Sale.objects.all()
    serializer_class = SaleRegistrationSerializer
    permission_classes = [IsAuthenticated, IsCustomer, CannotBeCarOwner]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        car_id = self.kwargs['pk']
        context['car'] = Car.objects.get(id=car_id)
        return context
    
    def create(self, request, *args, **kwargs):
        car = Car.objects.get(id=self.kwargs['pk'])
        self.check_object_permissions(request, car)
        return super().create(request, *args, **kwargs)

@extend_schema(tags=["Sales - Authenticated-Customer"])
class BuyerSalesListView(generics.ListAPIView):
    """
    Allow authenticated customers to view their sales list.
    """
    serializer_class = SaleDetailSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Sale.objects.filter(buyer=self.request.user.customer_profile)

@extend_schema(tags=["Sales - Authenticated-Customer"])
class OwnerSalesListView(generics.ListAPIView):
    """
    Allow authenticated owners to view their sales list.
    """
    serializer_class = SaleDetailSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Sale.objects.filter(seller=self.request.user.customer_profile)

@extend_schema(tags=["Sales - Authenticated-Employee"])
class StaffSalesListView(generics.ListAPIView):
    """
    Allow authenticated employees to view all sales.
    """
    queryset = Sale.objects.all()
    serializer_class = SaleDetailSerializer
    permission_classes = [IsAuthenticated, IsEmployeeActive]