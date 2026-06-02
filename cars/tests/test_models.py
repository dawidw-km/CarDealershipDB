from datetime import date
from django.test import TestCase
from django.core.exceptions import ValidationError
from ..models import (
    Car,
    VehicleType,
    FuelType,
    Transmission,
    VehicleCondition,
    AccidentStatus,
    Status,
    ModerationStatus,
    )
from person.models import Customer, Employee
from django.contrib.auth import get_user_model

User = get_user_model()

class CarTestCase(TestCase):

    def create_user(self, email):
        return User.objects.create_user(
            username=email,
            email=email,
            password='testpassword'
        )

    def create_customer(self, email):
        user = self.create_user(email)

        return Customer.objects.create(
            user=user,
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            address="Warszawska 12",
            date_of_birth=date(1990, 1, 1)
        )
    
    def create_employee_worker(self, email):
        user = self.create_user(email)
        return Employee.objects.create(
            user=user,
            first_name="Adam",
            last_name="Kowalski",
            email=email,
            phone_number="+48321321321",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1)
        )

    def create_car(self):

        customer = self.create_customer("testuser1@gmail.com")

        return  Car.objects.create(
            owner=customer,
            brand="Toyota",
            model="Corolla",
            color="Red",
            vehicle_type=VehicleType.SUV,
            year=2020,
            vin="1HGCM82633A004352",
            mileage=10000,
            fuel_type=FuelType.GASOLINE,
            transmission=Transmission.MANUAL,
            vehicle_condition=VehicleCondition.USED,
            accident_status=AccidentStatus.ACCIDENT_FREE,
            listing_price=10000,
            status=Status.AVAILABLE,
            description="This is a test car",
            moderation_status=ModerationStatus.PENDING,
            reviewer=None
        )

    
    def test_car_creation_is_valid(self):
        car = self.create_car()
        car.full_clean()
        car.save()
        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.model, "Corolla")
        self.assertEqual(car.color, "Red")
        self.assertEqual(car.vehicle_type, VehicleType.SUV)
        self.assertEqual(car.year, 2020)
        self.assertEqual(car.vin, "1HGCM82633A004352")
        self.assertEqual(car.mileage, 10000)
        self.assertEqual(car.fuel_type, FuelType.GASOLINE)
        self.assertEqual(car.transmission, Transmission.MANUAL)
        self.assertEqual(car.vehicle_condition, VehicleCondition.USED)
        self.assertEqual(car.accident_status, AccidentStatus.ACCIDENT_FREE)
        self.assertEqual(car.listing_price, 10000)
        self.assertEqual(car.status, Status.AVAILABLE)

    def test_car_creation_with_invalid_vehicle_type(self):
        car = self.create_car()
        car.vehicle_type = "invalid"
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_car_creation_with_negative_year(self):
        car = self.create_car()
        car.year = -1
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_car_creation_with_future_year(self):
        car = self.create_car()
        car.year = date.today().year + 1
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_invalid_vin_raises_validation_error(self):
        car = self.create_car()
        car.vin = "INVALID"

        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_mileage_cannot_exceed_max_value(self):
        car = self.create_car()
        car.mileage = 2000001

        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_description_cannot_exceed_500_chars(self):
        car = self.create_car()
        car.description = "a" * 501

        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_invalid_status_choice_raises_validation_error(self):
        car = self.create_car()
        car.status = "archived"

        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_str_returns_brand_model_and_year(self):
        car = self.create_car()

        self.assertEqual(str(car), "Toyota Corolla (2020)")

    def test_new_vehicle_must_be_accident_free(self):
        car = self.create_car()
        car.vehicle_condition = VehicleCondition.NEW
        car.accident_status = AccidentStatus.AFTER_IMPACT
        with self.assertRaises(ValidationError):
            car.full_clean()
    
    def test_new_vehicle_cannot_have_mileage_greater_than_100(self):
        car = self.create_car()
        car.vehicle_condition = VehicleCondition.NEW
        car.mileage = 101
        with self.assertRaises(ValidationError):
            car.full_clean()
    
    def test_new_vehicle_with_valid_data_passes_validation(self):
        car = self.create_car()

        car.vehicle_condition = VehicleCondition.NEW
        car.accident_status = AccidentStatus.ACCIDENT_FREE
        car.mileage = 50

        car.full_clean()

    def test_sold_vehicle_must_have_reviewer(self):
        car = self.create_car()
        car.status = Status.SOLD
        car.reviewer = None
        car.moderation_status = ModerationStatus.APPROVED
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_sold_vehicle_must_be_approved(self):
        car = self.create_car()
        car.status = Status.SOLD
        car.reviewer = self.create_employee_worker("testemployee1@gmail.com")
        car.moderation_status = ModerationStatus.PENDING
        with self.assertRaises(ValidationError):
            car.full_clean()
    
    def test_sold_vehicle_with_valid_data_passes_validation(self):
        car = self.create_car()
        car_buyer = self.create_customer("testcustomer11@gmail.com")
        car.status = Status.SOLD
        car.reviewer = self.create_employee_worker("testemployee1@gmail.com")
        car.moderation_status = ModerationStatus.APPROVED
        car.buyer = car_buyer
        car.full_clean()

    def test_listing_price_must_be_greater_than_0(self):
        car = self.create_car()
        car.listing_price = 0
        with self.assertRaises(ValidationError):
            car.full_clean()
    
    def test_listing_price_with_valid_data_passes_validation(self):
        car = self.create_car()
        car.listing_price = 10000
        car.full_clean()

    def test_sold_vehicle_cannot_be_bought_by_the_owner(self):
        car_reviewer = self.create_employee_worker("testemployee1@gmail.com")
        car = self.create_car()

        car.buyer = car.owner
        car.reviewer = car_reviewer
        car.moderation_status = ModerationStatus.APPROVED
        car.status = Status.SOLD

        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_sold_vehicle_must_have_a_buyer(self):
        car = self.create_car()
        car.status = Status.SOLD
        car.reviewer = self.create_employee_worker("testemployee1@gmail.com")
        car.moderation_status = ModerationStatus.APPROVED
        car.buyer = None
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_reserved_vehicle_must_have_a_buyer(self):
        car = self.create_car()
        car.status = Status.RESERVED
        car.reviewer = self.create_employee_worker("testemployee1@gmail.com")
        car.moderation_status = ModerationStatus.APPROVED
        car.buyer = None
        with self.assertRaises(ValidationError):
            car.full_clean()
    
    def test_reserved_vehicle_must_be_approved(self):
        car = self.create_car()
        car.status = Status.RESERVED
        car.reviewer = self.create_employee_worker("testemployee1@gmail.com")
        car.moderation_status = ModerationStatus.PENDING
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_reserved_vehicle_must_have_a_reviewer(self):
        car = self.create_car()
        car.status = Status.RESERVED
        car.buyer = self.create_customer("testcustomer11@gmail.com")
        car.moderation_status = ModerationStatus.APPROVED
        car.reviewer = None
        with self.assertRaises(ValidationError):
            car.full_clean()

    def test_reserved_vehicle_owner_cannot_be_the_buyer(self):
        car = self.create_car()
        employee = self.create_employee_worker("testemployee1@gmail.com")
        car.reviewer = employee
        car.status = Status.RESERVED
        car.buyer = car.owner
        car.moderation_status = ModerationStatus.APPROVED
        with self.assertRaises(ValidationError):
            car.full_clean()