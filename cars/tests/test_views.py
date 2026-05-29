from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Car, Status, ModerationStatus
from person.models import Customer, Employee
from datetime import date
from rest_framework import status

User = get_user_model()

class CarViewsTestCase(APITestCase):

    # Helper methods to create test data

    def create_user(self, email):
        return User.objects.create_user(
            username=email,
            email=email,
            password="testpass123"
        )
    
    def create_customer(self, email):
        user = self.create_user(email)
        return Customer.objects.create(
            user=user,
            first_name="Jan",
            last_name="Nowak",
            email=email,
            phone_number="+48123123123",
            address="Warszawa 12",
            date_of_birth=date(2000, 1, 1)
        )
    
    def create_employee_admin(self, email):
        user = self.create_user(email)
        return Employee.objects.create(
            user=user,
            first_name="Adam",
            last_name="Kowalski",
            email=email,
            phone_number="+48321321321",
            role=Employee.EmployeeRole.ADMIN,
            salary=5000,
            hire_date=date(2020, 1, 1)
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
        return Car.objects.create(
            owner=customer,
            brand="Toyota",
            model="Corolla",
            color="Red",
            vehicle_type="sedan",
            year=2020,
            vin="1HGCM82633A004352",
            mileage=100,
            fuel_type="gasoline",
            transmission="manual",
            vehicle_condition="new",
            accident_status="accident_free",
            listing_price=10000,
            description="This is a new car",
        )

    def get_valid_car_data(self):
        return {
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": "1HGCM82633A004352",
            "mileage": 100,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "new",
            "accident_status": "accident_free",
            "listing_price": 10000,
            "description": "This is a new car",
        }


    # Test cases

    def test_anonymous_user_cannot_register_car(self):
        response = self.client.post(
            reverse("car-registration"),
            self.get_valid_car_data(),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_anonymous_user_cannot_update_car(self):
        data = {
            "brand": "BMW"
        }
        car = self.create_car()
        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)