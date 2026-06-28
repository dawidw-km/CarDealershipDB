import factory
import random
from django.core.management.base import BaseCommand
from datetime import date
from django.contrib.auth import get_user_model
from person.models import Customer, Employee
from cars.models import (
    Car,
    VehicleType,
    FuelType,
    Transmission,
    VehicleCondition,
    AccidentStatus,
    Status,
    ModerationStatus,
)
from cars.tests.helpers import TestHelpers

User = get_user_model()

# CUSTOMER DATA
customer_email = "customer@customer.com"
customer_password = "Customer123"

#EMPLOYEE WORKER DATA
employee_worker_email = "worker@employee.com"
employee_worker_password = "Worker123"

#EMPLOYEE ADMIN DATA
employee_admin_email = "admin@employee.com"
employee_admin_password = "Admin123"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker('email')
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = factory.PostGenerationMethodCall('set_password', 'Testpass123')

class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker('first_name', locale='pl_PL')
    last_name = factory.Faker('last_name', locale='pl_PL')
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    phone_number = factory.LazyFunction(lambda: f"+48{random.randint(100000000, 999999999)}")
    address = factory.Faker('address', locale='pl_PL')
    date_of_birth = factory.Faker('date_of_birth', minimum_age=18, maximum_age=100)

class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker('first_name', locale='pl_PL')
    last_name = factory.Faker('last_name', locale='pl_PL')
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    phone_number = factory.LazyFunction(lambda: f"+48{random.randint(100000000, 999999999)}")
    role = factory.Iterator([Employee.EmployeeRole.WORKER, Employee.EmployeeRole.ADMIN])
    salary = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    hire_date = factory.Faker('date_this_decade', before_today=True, after_today=False)


BRANDS = [
    "Toyota", "BMW", "Audi", "Ford",
    "Volkswagen", "Skoda", "Mercedes", "Honda", "Nissan",
    "Hyundai", "Kia", "Chevrolet", "Jeep", "Subaru", "Volvo",
    "Land Rover", "Lexus", "Mazda", "Mercedes-Benz", "Mini",
    "Mitsubishi", "Peugeot", "Renault", "Skoda",
    "Suzuki", "Volkswagen"
]
MODELS = [
    "Corolla", "X5", "A4", "Focus", "Golf", "Octavia",
    "C-Class", "Civic", "Accord", "Camry", "Civic",
    "Corolla", "Focus", "Golf", "Honda", "HR-V", "Insight"
]

class CarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Car
        abstract = True

    owner = factory.SubFactory(CustomerFactory)
    brand = factory.Iterator(BRANDS)
    model = factory.Iterator(MODELS)
    color = factory.Faker('color_name')
    vehicle_type = factory.Iterator(VehicleType.values)
    year = factory.Faker('random_int', min=1950, max=date.today().year)
    vin = factory.Faker('vin')
    fuel_type = factory.Iterator(FuelType.values)
    transmission = factory.Iterator(Transmission.values)
    listing_price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    description = factory.Faker('sentence')

    @factory.post_generation
    def run_full_clean(self, create, extracted, **kwargs):
        if create:
            self.full_clean()
            self.save()

class NewCarFactory(CarFactory):
    vehicle_condition = VehicleCondition.NEW
    accident_status = AccidentStatus.ACCIDENT_FREE
    mileage = factory.Faker('random_int', min=0, max=100)

class UsedCarFactory(CarFactory):
    vehicle_condition = VehicleCondition.USED
    accident_status = AccidentStatus.ACCIDENT_FREE
    mileage = factory.Faker('random_int', min=100, max=2000000)

class DamagedCarFactory(CarFactory):
    vehicle_condition = VehicleCondition.FOR_PARTS
    accident_status = AccidentStatus.DAMAGED
    mileage = factory.Faker('random_int', min=5000, max=2000000)


class Command(BaseCommand, TestHelpers):
    help = 'Seed demo data for the application'

    def create_fixed_customer(self):
        if Customer.objects.filter(email=customer_email).exists():
            self.stdout.write("Customer already exists")
            return

        user = User.objects.create_user(
            username=customer_email,
            email=customer_email,
            password=customer_password
        )

        customer = Customer(
            user=user,
            first_name="Marek",
            last_name="Konieczny",
            email=customer_email,
            phone_number="+48123456789",
            address="Warszawa, Polska",
            date_of_birth=date(1995, 1, 1)
        )

        customer.full_clean()
        customer.save()
        self.stdout.write(self.style.SUCCESS(f'Created fixed customer: {customer}'))

    def create_fixed_employee_worker(self):
        if Employee.objects.filter(email=employee_worker_email).exists():
            self.stdout.write("Employee worker already exists")
            return

        user = User.objects.create_user(
            username=employee_worker_email,
            email=employee_worker_email,
            password=employee_worker_password
        )

        employee = Employee(
            user=user,
            first_name="Adam",
            last_name="Kowalski",
            email=employee_worker_email,
            phone_number="+48321321321",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1)
        )

        employee.full_clean()
        employee.save()
        self.stdout.write(self.style.SUCCESS(f'Created fixed employee worker: {employee}'))

    def create_fixed_employee_admin(self):
        if Employee.objects.filter(email=employee_admin_email).exists():
            self.stdout.write("Employee admin already exists")
            return

        user = User.objects.create_user(
            username=employee_admin_email,
            email=employee_admin_email,
            password=employee_admin_password
        )

        employee = Employee(
            user=user,
            first_name="Adam",
            last_name="Kowalski",
            email=employee_admin_email,
            phone_number="+48321321321",
            role=Employee.EmployeeRole.ADMIN,
            salary=5000,
            hire_date=date(2020, 1, 1)
        )

        employee.full_clean()
        employee.save()
        self.stdout.write(self.style.SUCCESS(f'Created fixed employee admin: {employee}'))

    def handle(self, *args, **options):
        self.create_fixed_customer()
        self.create_fixed_employee_worker()
        self.create_fixed_employee_admin()
        customers = CustomerFactory.create_batch(10)
        self.stdout.write(self.style.SUCCESS(f'Created {customers} customers'))
        employees = EmployeeFactory.create_batch(10)
        self.stdout.write(self.style.SUCCESS(f'Created {employees} employees'))
        customer = list(Customer.objects.all())
        employee = list(Employee.objects.all())

        # Create new cars
        new_cars = [NewCarFactory.create(
            owner=random.choice(customers)
            ) for _ in range(10)
        ]
        self.stdout.write(self.style.SUCCESS(f'Created {new_cars} new cars'))

        # Create used cars
        used_cars = [UsedCarFactory.create(
            owner=random.choice(customers)
            ) for _ in range(10)
        ]
        self.stdout.write(self.style.SUCCESS(f'Created {used_cars} used cars'))

        # Create damaged cars
        damaged_cars = [DamagedCarFactory.create(
            owner=random.choice(customers)
            ) for _ in range(10)
        ]
        self.stdout.write(self.style.SUCCESS(f'Created {damaged_cars} damaged cars'))

        # Approve cars by a random employee
        reviewer = random.choice(employees)
        approved_cars = [self.mark_car_as_approved(
            NewCarFactory.create(
                owner=random.choice(customers)),
                reviewer
            ) for _ in range(10)
        ]
        self.stdout.write(self.style.SUCCESS(f'Created {approved_cars} approved cars'))