from datetime import date
from django.core.exceptions import ValidationError
from django.test import TestCase
from ..serializers import (
    CarRegistrationSerializer,
    CarDetailUpdateSerializer,
    CarModerationStatusUpdateSerializer,
    CarSoftDeleteSerializer,
    ModerationStatusUpdateSerializerApproved,
    ModerationStatusUpdateSerializerRejected
)
from ..models import ModerationStatus
from person.models import Customer, Employee
from django.contrib.auth import get_user_model

User = get_user_model()

class CarRegistrationSerializerTestCase(TestCase):

    # Helper methods to create test data

    def create_user(self, email):
        """
        Creates a new user and returns the user object.
        """
        return User.objects.create_user(
            username=email,
            email=email,
            password="testpassword"
        )

    def create_customer(self, email):
        """
        Creates a new customer and returns the customer object.
        """
        user = self.create_user("testcustomer@example.com")

        return Customer.objects.create(
            user=user,
            first_name="John",
            last_name="Doe",
            email=email,
            phone_number="+48123456789",
            address="123 Main St, Anytown, USA",
            date_of_birth=date(1990, 1, 1)
        )

    def create_employee(self, email):
        """
        Creates a new employee and returns the employee object.
        """
        user = self.create_user("testemployee@example.com")

        return Employee.objects.create(
            user=user,
            first_name="John",
            last_name="Doe",
            email=email,
            phone_number="+48123456789",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1),
            employment_status=Employee.EmploymentStatus.ACTIVE
        )


    def create_valid_car_serializer(self):
        """
        Creates a serializer with valid car data.
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
        customer = self.create_customer("testcustomer@example.com")
        serializer = self.create_valid_car_serializer()

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
        data = {
            'year': 1880,
            'vin': "123456789012345Q7",
            'mileage': 2000001
        }

        serializer = self.create_valid_car_serializer()

        serializer.initial_data.update(data)
        
        serializer.is_valid()

        self.assertEqual(serializer.errors['year'][0], "Year of production cannot be earlier than 1886.")
        self.assertEqual(serializer.errors['vin'][0], "Invalid VIN format.")
        self.assertEqual(serializer.errors['mileage'][0], "Ensure this value is less than or equal to 2000000.")


    def test_car_detail_update_serializer_is_valid(self):
        customer = self.create_customer("testcustomer@example.com")
        employee = self.create_employee("testemployee@example.com")
        serializer = self.create_valid_car_serializer()
        serializer.is_valid()
        car = serializer.save(owner=customer)

        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

        serializer = ModerationStatusUpdateSerializerApproved(data={
            "moderation_status": ModerationStatus.APPROVED
        })
        serializer.is_valid()
        car = serializer.save(reviewer=employee)

        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertEqual(car.reviewer, employee)


