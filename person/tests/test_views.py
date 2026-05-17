from rest_framework.test import APITestCase, force_authenticate
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Customer, Employee
from datetime import date

User = get_user_model()

class PersonViewsTestCase(APITestCase):

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

        response = self.client.patch("/api/customer/me/", data, format="json")
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
        self.assertTrue(customer.user.check_password("newpass456"))

    def test_user_cannot_change_password_with_wrong_old_password(self):
        customer = self.create_customer("account@example.com")

        self.client.force_authenticate(user=customer.user)

        data = {
            "old_password": "wrongpass",
            "new_password": "newpass456"
        }
        response = self.client.put("/api/change-password/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_change_password_to_same_password(self):
        customer = self.create_customer("account@example.com")

        self.client.force_authenticate(user=customer.user)

        data = {
            "old_password": "testpass123",
            "new_password": "testpass123"
        }
        response = self.client.put("/api/change-password/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_employee_can_update_employee_profile(self):

        admin = self.create_employee_admin("jack.reacher@example.com")
        employee = self.create_employee_worker("mike.Tyson@example.com")

        self.client.force_authenticate(user=admin.user)

        employee_id = employee.id

        data = {
            "first_name": "Jayce",
            "last_name": "Arcane",
            "phone_number": "+48765432109"
        }

        response = self.client.patch(
            reverse("admin-employee-update", args=[employee_id]),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        employee.refresh_from_db()

        self.assertEqual(employee.first_name, "Jayce")
        self.assertEqual(employee.last_name, "Arcane")
        self.assertEqual(employee.phone_number, "+48765432109")

    
    def test_non_admin_employee_cannot_update_employee_profile(self):

        employee1 = self.create_employee_worker("worker@example.com")
        employee2 = self.create_employee_worker("worker2@example.com")

        self.client.force_authenticate(user=employee1.user)

        employee_id = employee2.id

        data = {
            "first_name": "Jayce",
            "last_name": "Arcane",
            "phone_number": "+48765432109"
        }

        response = self.client.patch(
            reverse("admin-employee-update", args=[employee_id]),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        employee2.refresh_from_db()

        self.assertEqual(employee2.first_name, "Adam")
        self.assertEqual(employee2.last_name, "Kowalski")
        self.assertEqual(employee2.phone_number, "+48321321321")

    def test_admin_employee_employment_status_change_on_update(self):

        admin = self.create_employee_admin("admin@example.com")

        employee = self.create_employee_worker("worker@example.com")

        self.client.force_authenticate(user=admin.user)

        employee_id = employee.id

        data = {
            "employment_status": Employee.EmploymentStatus.INACTIVE,
            "layoff_date": "2024-01-01"
        }

        response = self.client.patch(
            reverse("admin-employee-employment-status-update", args=[employee_id]),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        employee.refresh_from_db()

        self.assertEqual(employee.employment_status, Employee.EmploymentStatus.INACTIVE)
        self.assertEqual(employee.layoff_date, date(2024, 1, 1))

    
    def test_non_admin_employee_cannot_change_employment_status(self):

        employee1 = self.create_employee_worker("worker1@gmail.com")
        employee2 = self.create_employee_worker("worker2@gmail.com")

        self.client.force_authenticate(user=employee1.user)

        employee_id = employee2.id

        data = {
            "employment_status": Employee.EmploymentStatus.INACTIVE,
            "layoff_date": "2024-01-01"
        }

        response = self.client.patch(
            reverse("admin-employee-employment-status-update", args=[employee_id]),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        employee2.refresh_from_db()

        self.assertEqual(employee2.employment_status, Employee.EmploymentStatus.ACTIVE)


    def test_inactive_employee_cannot_sign_in(self):
        user = self.create_user("inactive@example.com")

        Employee.objects.create(
            user=user,
            first_name="Adam",
            last_name="Kowalski",
            email="inactive@example.com",
            phone_number="+48321321321",
            role=Employee.EmployeeRole.ADMIN,
            salary=5000,
            hire_date=date(2020, 1, 1),
            employment_status=Employee.EmploymentStatus.INACTIVE,
            layoff_date=date(2024, 1, 1),
        )

        response = self.client.post(
            reverse("employee-token-obtain-pair"),
            {
                "username": "inactive@example.com",
                "password": "testpass123",
            },  
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Your employee account is inactive.")


    def test_active_employee_can_sign_in(self):
        employee = self.create_employee_admin("active@example.com")

        self.client.force_authenticate(user=employee.user)

        response = self.client.post(
            reverse("employee-token-obtain-pair"),
            {
                "username": "active@example.com",
                "password": "testpass123",
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_employee_can_access_own_profile(self):
        employee = self.create_employee_worker("employee@example.com")
        self.client.force_authenticate(user=employee.user)

        response = self.client.get(
            reverse("employee-detail"),
            {
                "username": "employee@example.com",
                "password": "testpass123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Adam")


    
    def test_non_employee_user_cannot_access_api_employee_me(self):
        customer = self.create_customer("customer@example.com")
        self.client.force_authenticate(user=customer.user)

        response = self.client.get(
            reverse("employee-detail"),
            {
                "username": "customer@example.com",
                "password": "testpass123"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_anonymous_user_cannot_access_employee_me(self):
        response = self.client.get(
            reverse("employee-detail")
            )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_anonymous_user_cannot_access_admin_employee_list(self):
        response = self.client.get(
            reverse("employee-list")
            )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)