from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from ..serializers import (
    CarRegistrationSerializer,
    CarDetailUpdateSerializer,
    CarModerationStatusUpdateSerializer,
    CarSoftDeleteSerializer
)
from person.models import Customer
from django.contrib.auth import get_user_model

User = get_user_model()

class CarRegistrationSerializerTestCase(TestCase):

    # Helper methods to create test data

    def create_customer(self):
        """
        Creates a new customer user and returns the customer object.
        """
        user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        return Customer.objects.create(
            user=user,
            first_name="John",
            last_name="Doe",
            email="testuser@example.com",
            phone_number="+48123456789",
            address="123 Main St, Anytown, USA",
            date_of_birth=date(1990, 1, 1)
        )

    def create_car(self):
        """
        Creates a new car object and returns the car object.
        """
        return CarRegistrationSerializer(data={
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": "12345678901234567",
            "mileage": 10000,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "used",
            "accident_status": "accident_free",
            "listing_price": 10000,
            "description": "This is a test car",
        })
    # Test cases

    def test_car_registration_serializer_is_valid(self):
        customer = self.create_customer()
        serializer = self.create_car()

        self.assertTrue(serializer.is_valid(), serializer.errors)

        car = serializer.save(owner=customer)

        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.model, "Corolla")
        self.assertEqual(car.color, "Red")
        self.assertEqual(car.vehicle_type, "sedan")
        self.assertEqual(car.year, 2020)
        self.assertEqual(car.vin, "12345678901234567")
        self.assertEqual(car.mileage, 10000)
        self.assertEqual(car.fuel_type, "gasoline")
        self.assertEqual(car.transmission, "manual")
        self.assertEqual(car.vehicle_condition, "used")
        self.assertEqual(car.accident_status, "accident_free")
        self.assertEqual(car.listing_price, 10000)
        self.assertEqual(car.description, "This is a test car")


    def test_car_registration_serializer_with_invalid_data(self):
        customer = self.create_customer()
        serializer = self.create_car()
        serializer.initial_data['year'] = -1
        serializer.initial_data['vin'] = "INVALID"
        serializer.initial_data['mileage'] = 2000001
        serializer.initial_data['mileage'] = -1
        serializer.is_valid(raise_exception=True)
        with self.assertRaises(ValidationError):
            serializer.save(owner=customer)
        self.assertEqual(serializer.errors['year'][0], "Year of production cannot be earlier than 1886.")
        self.assertEqual(serializer.errors['vin'][0], "Invalid VIN format.")
        self.assertEqual(serializer.errors['mileage'][0], "Ensure this value is less than or equal to 2000000.")
        self.assertEqual(serializer.errors['mileage'][0], "Ensure this value is greater than or equal to 0.")
 