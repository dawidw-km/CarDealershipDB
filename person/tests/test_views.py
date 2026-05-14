from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Customer, Employee
from datetime import date

User = get_user_model()

class CustomerViewsTestCase(APITestCase):

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
        phone_number="123123123",
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
        phone_number="321321321",
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
        phone_number="321321321",
        role=Employee.EmployeeRole.WORKER,
        salary=5000,
        hire_date=date(2020, 1, 1)
    )
 
# Test cases

    def test_anonymous_user_can_create_customer_account(self):
        data = {
            "first_name": "Dawid",
            "last_name": "Konieczny",
            "email": "dawid.konieczny@example.com",
            "phone_number": "+48123456789",
            "address": "Warszawa 12",
            "date_of_birth": "2000-01-01",
            "password": "testpass123"
        }

        response = self.client.post("/api/register/customer/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="dawid.konieczny@example.com").exists())
        self.assertTrue(Customer.objects.filter(email="dawid.konieczny@example.com").exists())

    
    def test_logged_in_user_cannot_create_customer_account(self):
        customer = self.create_customer("existing1@gmail.com")
        self.client.force_authenticate(user=customer.user)

        data = {
            "first_name": "Dawid",
            "last_name": "Niekonieczny",
            "email": "existing2@gmail.com",
            "phone_number": "+48987654321",
            "address": "Kraków 34",
            "date_of_birth": "1995-05-05",
            "password": "testpass123"
        }

        response = self.client.post("/api/register/customer/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    
    def test_customer_can_access_own_profile(self):
        customer = self.create_customer("customer@example.com")
        self.client.force_authenticate(user=customer.user)

        response = self.client.get("/api/customer/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_customer_can_update_own_profile_with_allowed_fields(self):
        customer = self.create_customer("customer@example.com")
        self.client.force_authenticate(user=customer.user)

        data = {
            "first_name": "Michał",
            "last_name": "Złotnicki",
            "phone_number": "+48535397213",
            "address": "Gdańsk 56"
        }

        response = self.client.put("/api/customer/me/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_customer_cannot_change_read_only_fields(self):
        customer = self.create_customer("customer@example.com")
        self.client.force_authenticate(user=customer.user)

        data = {
            "email": "different@example.com"
        }

        response = self.client.patch("/api/customer/me/", data, format="json")

        customer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(customer.email, "customer@example.com")

    
    def test_non_admin_employee_cannot_create_admin_employee(self):
        employee = self.create_employee_worker("worker@example.com")
        self.client.force_authenticate(user=employee.user)

        data = {
            "first_name": "Oskar",
            "last_name": "Aleksandrzak",
            "email": "oskar.aleksandrzak@example.com",
            "phone_number": "+48765432109",
            "role": Employee.EmployeeRole.ADMIN,
            "salary": 4000,
            "hire_date": "2021-01-01",
            "password": "testpass123"
        }

        response = self.client.post("/api/register/employee/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Employee.objects.filter(email="oskar.aleksandrzak@example.com").exists())

    
    def test_admin_employee_can_create_admin_employee(self):
        employee = self.create_employee_admin("admin@example.com")
        self.client.force_authenticate(user=employee.user)

        data = {
            "first_name": "Oskar",
            "last_name": "Aleksandrzak",
            "email": "oskar.aleksandrzak@example.com",
            "phone_number": "+48765432109",
            "role": Employee.EmployeeRole.ADMIN,
            "salary": 4000,
            "hire_date": "2021-01-01",
            "password": "testpass123"
        }

        response = self.client.post("/api/register/employee/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Employee.objects.filter(email="oskar.aleksandrzak@example.com").exists())

    
    def test_admin_employee_can_list_employees(self):
        employee = self.create_employee_admin("admin@example.com")
        self.client.force_authenticate(user=employee.user)

        self.create_employee_worker("worker@example.com")

        response = self.client.get("/api/admin/employees/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_can_change_own_password(self):
        customer = self.create_customer("jackreacher@example.com")

        self.client.force_authenticate(user=customer.user)

        data = {
            "old_password": "testpass123",
            "new_password": "newpass456"
        }

        response = self.client.put("/api/change-password/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)