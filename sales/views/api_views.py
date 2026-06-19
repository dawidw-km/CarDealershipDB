from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from sales.models import Sale
from sales.serializers import SaleRegistrationSerializer, SaleDetailSerializer
from person.permissions import IsCustomer
from drf_spectacular.utils import extend_schema
from django.urls import reverse
from cars.models import Car

@extend_schema(tags=["Sales - Authenticated-Customer"])
class SaleRegistrationView(generics.CreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleRegistrationSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        car_id = self.kwargs['pk']
        context['car'] = Car.objects.get(id=car_id)
        return context