from django.contrib.auth import get_user_model
from person.models import Customer, Employee
from cars.models import Car, ModerationStatus, Status
from datetime import date

User = get_user_model()

class TestHelpers:

    def create_user(self, email):
        return User.objects.create_user(
            username=email,
            email=email,
            password="testpass123"
        )

    def create_superuser(self, email):
        return User.objects.create_superuser(
            username=email,
            email=email,
            password="testpass123"
        )

    def create_customer(self, email):
        user = self.create_user(email)
        customer = Customer(
            user=user,
            first_name="Jan",
            last_name="Nowak",
            email=email,
            phone_number="+48123123123",
            address="Warszawa 12",
            date_of_birth=date(2000, 1, 1)
        )
        customer.full_clean()
        customer.save()
        return customer

    def create_employee_admin(self, email):
        user = self.create_user(email)
        employee = Employee(
            user=user,
            first_name="Adam",
            last_name="Kowalski",
            email=email,
            phone_number="+48321321321",
            role=Employee.EmployeeRole.ADMIN,
            salary=5000,
            hire_date=date(2020, 1, 1)
        )
        employee.full_clean()
        employee.save()
        return employee

    def create_employee_worker(self, email):
        user = self.create_user(email)
        employee = Employee(
            user=user,
            first_name="Adam",
            last_name="Kowalski",
            email=email,
            phone_number="+48321321321",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1)
        )
        employee.full_clean()
        employee.save()
        return employee

    def create_car(self, owner=None):
        if owner is None:
            owner = self.create_customer("unique_owner@gmail.com")
        car = Car(
            owner=owner,
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
        car.full_clean()
        car.save()
        return car

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

    def mark_car_as_approved(self, car, reviewer=None):
        car.moderation_status = ModerationStatus.APPROVED
        car.reviewer = reviewer if reviewer is not None else self.create_employee_worker("employee_approve_car@gmail.com")
        car.full_clean()
        car.save()
        return car

    def mark_car_as_sold(self, car, buyer=None):
        """
        Marks a car as sold. It has to be approved by a reviewer first.
        """
        car.status = Status.SOLD
        car.buyer = buyer if buyer is not None else self.create_customer("customer_buy_car@gmail.com")
        car.full_clean()
        car.save()
        return car
    
    def mark_car_as_reserved(self, car, buyer=None):
        """
        Marks a car as reserved. It has to be approved by a reviewer first.
        """
        car.status = Status.RESERVED
        car.buyer = buyer if buyer is not None else self.create_customer("customer_reserve_car@gmail.com")
        car.full_clean()
        car.save()
        return car
    
    def mark_employee_as_inactive(self, employee):
        employee.employment_status = Employee.EmploymentStatus.INACTIVE
        employee.layoff_date = date(2020, 1, 1)
        employee.full_clean()
        employee.save()
        return employee

    def mark_car_as_deleted(self, car):
        car.is_deleted = True
        car.save()
        return car
        