from datetime import date
from rest_framework.exceptions import ValidationError
from django.http import HttpRequest
from django.test import TestCase
from ..serializers import (
    CarRegistrationSerializer,
    CarDetailUpdateSerializer,
    ModerationStatusUpdateSerializerApproved,
    ModerationStatusUpdateSerializerRejected,
    CarSoftDeleteSerializer
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

    def request_with_user(self, user):
        request = HttpRequest()
        request.user = user
        return request

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
            "year": 1880,
            "vin": "123456789012345Q7",
            "mileage": 2000001
        }

        serializer = self.create_valid_car_serializer()

        serializer.initial_data.update(data)
        
        serializer.is_valid()

        self.assertEqual(serializer.errors["year"][0], "Year of production cannot be earlier than 1886.")
        self.assertEqual(serializer.errors["vin"][0], "Invalid VIN format.")
        self.assertEqual(serializer.errors["mileage"][0], "Ensure this value is less than or equal to 2000000.")


    def test_car_moderation_status_update_serializer_approved(self):
        customer = self.create_customer("testcustomer@example.com")
        employee = self.create_employee("testemployee@example.com")
        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

        request = HttpRequest()
        request.user = employee.user

        serializer_approved = ModerationStatusUpdateSerializerApproved(car, context={"request": request}, data={
            "moderation_status": ModerationStatus.APPROVED
        })
        serializer_approved.is_valid(raise_exception=True)
        updated_car = serializer_approved.save()

        self.assertEqual(updated_car.moderation_status, ModerationStatus.APPROVED)
        self.assertEqual(updated_car.reviewer, employee)

    
    def test_car_moderation_status_update_serializer_rejected(self):
        customer = self.create_customer("testcustomer@example.com")
        employee = self.create_employee("testemployee@example.com")
        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

        request = HttpRequest()
        request.user = employee.user

        serializer_rejected = ModerationStatusUpdateSerializerRejected(car, context={"request": request}, data={
            "moderation_status": ModerationStatus.REJECTED
        })
        serializer_rejected.is_valid(raise_exception=True)
        updated_car = serializer_rejected.save()

        self.assertEqual(updated_car.moderation_status, ModerationStatus.REJECTED)
        self.assertEqual(updated_car.reviewer, employee)

    
    def test_car_moderation_status_cannot_be_updated_by_non_employee(self):
        customer = self.create_customer("testcustomer@example.com")
        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        request = HttpRequest()
        request.user = customer.user

        serializer_approved = ModerationStatusUpdateSerializerApproved(car, context={"request": request}, data={
            "moderation_status": ModerationStatus.APPROVED
        })

        serializer_approved.is_valid(raise_exception=True)
        with self.assertRaises(ValidationError):
            serializer_approved.save()

        car.refresh_from_db()

        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)


    def test_car_updated_resets_moderation_status_on_critical_change(self):
        customer = self.create_customer("testcustomer@example.com")
        employee = self.create_employee("testemployee@example.com")

        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        request = self.request_with_user(employee.user)

        serializer_approved = ModerationStatusUpdateSerializerApproved(car, context={"request": request}, data={
            "moderation_status": ModerationStatus.APPROVED
        })
        serializer_approved.is_valid(raise_exception=True)
        updated_car = serializer_approved.save()
        self.assertEqual(updated_car.moderation_status, ModerationStatus.APPROVED)

        update_data = {
            "brand": "BMW",
        }

        customer_request = self.request_with_user(customer.user)

        serializer_update = CarDetailUpdateSerializer(
            updated_car,
            context={"request": customer_request},
            data=update_data,
            partial=True
        )

        serializer_update.is_valid(raise_exception=True)
        updated_car = serializer_update.save()

        self.assertEqual(updated_car.brand, "BMW")

        updated_car.refresh_from_db()

        self.assertEqual(updated_car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(updated_car.reviewer, None)

    
    def test_car_updated_with_non_critical_moderation_fields_has_no_effect_on_moderation_status(self):
        customer = self.create_customer("testcustomer@example.com")
        employee = self.create_employee("testemployee@example.com")

        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        request = self.request_with_user(employee.user)
        

        serializer_approved = ModerationStatusUpdateSerializerApproved(car, context={"request": request}, data={
            "moderation_status": ModerationStatus.APPROVED
        })
        serializer_approved.is_valid(raise_exception=True)
        updated_car = serializer_approved.save()
        self.assertEqual(updated_car.moderation_status, ModerationStatus.APPROVED)

        update_data = {
            "description": "Reacher is a great series.",
        }
        
        customer_request = self.request_with_user(customer.user)

        serializer_update = CarDetailUpdateSerializer(
            updated_car,
            context={"request": customer_request},
            data=update_data,
            partial=True
        )

        serializer_update.is_valid(raise_exception=True)
        updated_car = serializer_update.save()

        updated_car.refresh_from_db()

        self.assertEqual(updated_car.description, "Reacher is a great series.")
        self.assertEqual(updated_car.moderation_status, ModerationStatus.APPROVED)
        self.assertEqual(updated_car.reviewer, employee)

    
    def test_car_update_serializer_no_moderation_status_change_on_the_same_data(self):
        customer = self.create_customer("testcustomer@example.com")
        employee = self.create_employee("testemployee@example.com")

        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)
        
        request = self.request_with_user(employee.user)

        serializer_approved = ModerationStatusUpdateSerializerApproved(
            car,
            context={"request": request},
            data={"moderation_status": ModerationStatus.APPROVED}
        )
        
        serializer_approved.is_valid(raise_exception=True)
        updated_car = serializer_approved.save()
        self.assertEqual(updated_car.moderation_status, ModerationStatus.APPROVED)

        data = {
            "brand": "Toyota",
        }
        
        customer_request = self.request_with_user(customer.user)

        serializer_update = CarDetailUpdateSerializer(
            updated_car,
            context={"request": customer_request},
            data=data,
            partial=True
        )

        serializer_update.is_valid(raise_exception=True)
        updated_car = serializer_update.save()
        
        updated_car.refresh_from_db()

        self.assertEqual(updated_car.brand, "Toyota")
        self.assertEqual(updated_car.moderation_status, ModerationStatus.APPROVED)
        self.assertEqual(updated_car.reviewer, employee)

    def test_car_updated_with_invalid_data_raises_validation_error(self):
        customer = self.create_customer("testcustomer@example.com")

        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        data = {
            "vehicle_condition": "new",
            "accident_status": "after_impact",
        }

        request = self.request_with_user(customer.user)

        serializer_update = CarDetailUpdateSerializer(
            car,
            context={"request": request},
            data=data,
            partial=True
        )

        with self.assertRaises(ValidationError):
            serializer_update.is_valid(raise_exception=True)
            serializer_update.save()

        car.refresh_from_db()

        self.assertEqual(car.vehicle_condition, "used")
        self.assertEqual(car.accident_status, "accident_free")

    
    def test_car_soft_delete_serializer_is_valid(self):
        customer = self.create_customer("testcustomer@example.com")
        serializer = self.create_valid_car_serializer()
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        request = self.request_with_user(customer.user)
        
        serializer_soft_delete = CarSoftDeleteSerializer(car, context={"request": request}, data={
            "is_deleted": True
        })

        serializer_soft_delete.is_valid(raise_exception=True)
        updated_car = serializer_soft_delete.save()

        self.assertEqual(updated_car.is_deleted, True)

    
    def test_car_registration_serializer_with_read_only_field_is_ignored(self):

        data = {
            "id": 999
        }

        customer = self.create_customer("testcustomer@example.com")
        serializer = self.create_valid_car_serializer()
        serializer.initial_data.update(data)
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        self.assertFalse(car.id == 999)

    
    def test_car_registration_read_only_owner_is_ignored(self):
        data = {
            "owner": 999
        }

        customer = self.create_customer("testcustomer@example.com")
        serializer = self.create_valid_car_serializer()
        serializer.initial_data.update(data)
        serializer.is_valid(raise_exception=True)
        car = serializer.save(owner=customer)

        self.assertFalse(car.owner == 999)


    def test_car_serializer_vin_uniqueness(self):
        customer = self.create_customer("testcustomer@example.com")
        car_serializer_1 = self.create_valid_car_serializer()
        car_serializer_1.is_valid(raise_exception=True)
        car_1 = car_serializer_1.save(owner=customer)

        car_2_serializer = CarRegistrationSerializer(data={
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": car_1.vin,
            "mileage": 10000,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "used",
            "accident_status": "accident_free",
            "listing_price": 10000,
        })

        with self.assertRaises(ValidationError):
            car_2_serializer.is_valid(raise_exception=True)


    