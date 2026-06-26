from django.core.management.base import BaseCommand
from datetime import date
import factory
import random
from django.contrib.auth import get_user_model
from person.models import Customer, Employee

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

class Command(BaseCommand):
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
