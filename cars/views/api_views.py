from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample
from cars.models import Car, ModerationStatus
from cars.serializers import (
    CarRegistrationSerializer,
    CarDetailUpdateSerializer,
    CarDetailSerializer,
    CarSoftDeleteSerializer,
    ModerationStatusUpdateSerializerApproved,
    ModerationStatusUpdateSerializerRejected,
    CarPurchaseStatusUpdateSerializerSold,
    CarPurchaseStatusUpdateSerializerReserved,
)
from person.permissions import IsCustomer
from cars.permissions import (
    IsCarOwnerOrSuperuser,
    CanChangeCarModerationStatus,
    CannotDeleteSoldCar,
    CannotModifySoldCar,
    CanViewOwnOrStaffCar,
    CannotBeCarOwner,
)
from person.permissions import IsEmployeeActive


@extend_schema(tags=["Cars - Authenticated-Customer"], examples=[
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
    Allow authenticated customers to register a new car.
    """
    queryset = Car.objects.all()
    serializer_class = CarRegistrationSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.customer_profile)


@extend_schema(tags=["Cars - Owner & Superuser"])
class CarDetailUpdateView(generics.UpdateAPIView):
    """
    Allow owner to update their own car details.
    Allow superuser to update any car details.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarDetailUpdateSerializer
    permission_classes = [IsAuthenticated, IsCarOwnerOrSuperuser, CannotModifySoldCar]

@extend_schema(tags=["Cars - Owner & Staff & Superuser"])
class OwnerOrStaffOrSuperuserAllCarsDetailView(generics.RetrieveAPIView):
    """
    Allow owners to retrieve details of their own car.
    Allow employees to retrieve any car.
    Allow superusers to retrieve any car.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarDetailSerializer
    permission_classes = [IsAuthenticated, CanViewOwnOrStaffCar]

@extend_schema(tags=["Cars - Details"])
class AllCarsDetailView(generics.RetrieveAPIView):
    """
    Allow all users to retrieve details of any car.
    """
    queryset = Car.objects.filter(is_deleted=False, moderation_status=ModerationStatus.APPROVED)
    serializer_class = CarDetailSerializer
    permission_classes = [AllowAny]

@extend_schema(tags=["Cars - Owner & Superuser"])
class CarSoftDeleteView(generics.UpdateAPIView):
    """
    Allow customer to soft delete their own car.
    Allow superuser to soft delete any car.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarSoftDeleteSerializer
    permission_classes = [IsAuthenticated, IsCarOwnerOrSuperuser, CannotDeleteSoldCar]

@extend_schema(tags=["Cars - Staff"])
class CarModerationStatusUpdateViewApproved(generics.UpdateAPIView):
    """
    Allow employees to update the moderation status of a car to approved.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = ModerationStatusUpdateSerializerApproved
    permission_classes = [IsAuthenticated, IsEmployeeActive, CanChangeCarModerationStatus]

@extend_schema(tags=["Cars - Staff"])
class CarModerationStatusUpdateViewRejected(generics.UpdateAPIView):
    """
    Allow employees to update the moderation status of a car to rejected.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = ModerationStatusUpdateSerializerRejected
    permission_classes = [IsAuthenticated, IsEmployeeActive, CanChangeCarModerationStatus]

@extend_schema(tags=["Cars - Authenticated-Customer"])
class CarPurchaseStatusUpdateViewSold(generics.UpdateAPIView):
    """
    Allow authenticated customers to update the purchase status of a car to sold.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarPurchaseStatusUpdateSerializerSold
    permission_classes = [IsAuthenticated, CannotBeCarOwner]

@extend_schema(tags=["Cars - Authenticated-Customer"])
class CarPurchaseStatusUpdateViewReserved(generics.UpdateAPIView):
    """
    Allow authenticated users to update the purchase status of a car to reserved.
    """
    queryset = Car.objects.filter(is_deleted=False)
    serializer_class = CarPurchaseStatusUpdateSerializerReserved
    permission_classes = [IsAuthenticated, CannotBeCarOwner]

@extend_schema(tags=["Cars - Staff & Superuser"])
class CarDetailForSoftDeleteView(generics.RetrieveAPIView):
    """
    Allow employees and superusers to retrieve details of a car that is soft deleted.
    """
    queryset = Car.objects.filter(is_deleted=True)
    serializer_class = CarDetailSerializer
    permission_classes = [IsAuthenticated, IsEmployeeActive]