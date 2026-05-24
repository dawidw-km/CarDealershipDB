from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample 
from cars.models import Car
from cars.serializers import (
    CarRegistrationSerializer,
    CarDetailUpdateSerializer,
    CarModerationStatusUpdateSerializer,
    CarDetailSerializer,
    CarSoftDeleteSerializer,
)
from person.permissions import IsCustomer
from cars.permissions import (
    IsCarOwnerOrSuperuser,
    CanChangeCarModerationStatus,
    CannotDeleteSoldCar,
    CannotModifySoldCar,
    CanViewCar,
)
from person.permissions import IsEmployeeActive

@extend_schema(tags=["Cars"], examples=[
    OpenApiExample(
        name="Car registration",
        value={
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": "12345678901234567",
            "mileage": 100,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "new",
            "accident_status": "accident_free",
            "listing_price": 10000.00,
            "description": "This is a new car",
        },
        request_only=True,
    )
])
class CarRegistrationView(generics.CreateAPIView):
    """
    Allow customers to register a new car.
    """
    queryset = Car.objects.all()
    serializer_class = CarRegistrationSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.customer_profile)


@extend_schema(tags=["Cars"])
class CarDetailUpdateView(generics.UpdateAPIView):
    """
    Allow customers to update their own car details.
    Allow superuser to update any car details.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarDetailUpdateSerializer
    permission_classes = [IsAuthenticated, IsCarOwnerOrSuperuser, CannotModifySoldCar]

@extend_schema(tags=["Cars"])
class CarDetailView(generics.RetrieveAPIView):
    """
    Allow customers to retrieve details of their own car.
    Allow employees and superuser to retrieve details of any car.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarDetailSerializer
    permission_classes = [IsAuthenticated, CanViewCar]

@extend_schema(tags=["Cars"])
class CarSoftDeleteView(generics.UpdateAPIView):
    """
    Allow customer to soft delete their own car.
    Allow superuser to soft delete any car.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarSoftDeleteSerializer
    permission_classes = [IsAuthenticated, IsCarOwnerOrSuperuser, CannotDeleteSoldCar]

@extend_schema(tags=["Cars/Employees"])
class CarModerationStatusUpdateView(generics.UpdateAPIView):
    """
    Allow employees to update the moderation status of a car.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarModerationStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsEmployeeActive, CanChangeCarModerationStatus]