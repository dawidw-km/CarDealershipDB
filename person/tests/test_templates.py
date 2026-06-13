from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Customer, Employee

User = get_user_model()


class PersonTemplateViewsTestCase(TestCase):

    # Helper methods to create test data

    def create_user(self, email):

        return User.objects.create_user(
            username=email,
            email=email,
            password="testpassword"
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
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            role=Employee.EmployeeRole.WORKER,
            salary=5000,
            hire_date=date(2020, 1, 1),
        )
    
    def create_employee_admin(self, email):
        
        user = self.create_user(email)

        return Employee.objects.create(
            user=user,
            first_name="Jack",
            last_name="Reacher",
            email=email,
            phone_number="+48123456789",
            role=Employee.EmployeeRole.ADMIN,
            salary=5000,
            hire_date=date(2020, 1, 1)
        )
    
    def create_superuser(self, email):
        return User.objects.create_superuser(
            username=email,
            email=email,
            password="testpassword"
        )

    # Test cases

    def test_logged_user_can_access_customer_profile(self):
        
        self.create_customer("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.get(
            reverse("customer-profile")
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "person/customer_profile.html"
        )

        self.assertIn(
            "customer",
            response.context
        )


    def test_logged_user_can_update_customer_profile(self):

        self.create_customer("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.post(
            reverse("customer-profile-update"),
            {
                "first_name": "Jacek",
            }
        )

        self.assertRedirects(
            response,
            reverse("customer-profile")
        )

        self.assertTrue(
            Customer.objects.filter(
                first_name="Jacek"
            ).exists()
        )
    
    
    def test_not_logged_user_cannot_update_customer_profile(self):

        self.create_customer("jack.reacher@example.com")

        response = self.client.post(
            reverse("customer-profile-update"),
            {
                "first_name": "Jacek",
            }
        )

        self.assertRedirects(
            response,
            "/login/form/?next=/customer/profile/update/"
        )
    
        self.assertFalse(
            Customer.objects.filter(
                first_name = "Jacek"
            ).exists()
        )

    
    def test_logged_user_can_change_password(self):

        self.create_customer("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.post(
            reverse("user-change-password"),
            {
                "old_password": "testpassword",
                "new_password": "newtestpassword",
            }
        )

        self.assertRedirects(
            response,
            reverse("customer-profile")
        )
        user = User.objects.get(email="jack.reacher@example.com")
        self.assertTrue(user.check_password("newtestpassword"))

    def test_logged_user_cannot_change_password_with_wrong_old_password(self):

        self.create_customer("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.post(
            reverse("user-change-password"),
            {
                "old_password": "wrongpassword",
                "new_password": "newtestpassword",
            }
        )
        
        self.assertIn("old_password", response.context["errors"])


    def test_not_logged_user_cannot_change_password(self):

        self.create_customer("jack.reacher@example.com")

        response = self.client.post(
            reverse("user-change-password"),
            {
                "old_password": "testpassword",
                "new_password": "newtestpassword",
            }
        )

        self.assertRedirects(
            response,
            "/login/form/?next=/user/change-password/"
        )
    

    def test_employee_can_access_employee_profile(self):
        self.create_employee_worker("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.get(
            reverse("employee-profile")
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "person/employee_profile.html"
        )

        self.assertIn(
            "employee",
            response.context
        )
    

    def test_not_admin_employee_cannot_access_employee_list(self):
        self.create_employee_worker("worker1@example.com")

        self.client.login(
            username="worker1@example.com",
            password="testpassword"
        )

        response = self.client.get(
            reverse("employee-list-template")
        )

        self.assertEqual(response.status_code, 403)

    
    def test_admin_employee_can_access_employee_list(self):
        self.create_employee_admin("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )
        
        response = self.client.get(
            reverse("employee-list-template")
        )

        self.assertEqual(response.status_code, 200)

    
    def test_admin_employee_can_update_employee_profile(self):
        self.create_employee_admin("jack.reacher@example.com")

        worker = self.create_employee_worker("worker@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.post(
            reverse("admin-employee-update-template", kwargs={"pk": worker.pk}),
            {
                "first_name": "Jayce",
                "last_name": "Arcane",
                "phone_number": "+48765432109",
                "role": Employee.EmployeeRole.WORKER,
                "salary": 5000,
                "hire_date": date(2020, 1, 1)
            }
        )

        self.assertRedirects(
            response,
            reverse("employee-list-template")
        )

        worker.refresh_from_db()

        self.assertEqual(worker.first_name, "Jayce")
        self.assertEqual(worker.last_name, "Arcane")


    def test_not_admin_employee_cannot_update_employee_profile(self):
        self.create_employee_worker("worker1@example.com")
        worker2 = self.create_employee_worker("worker2@example.com")

        self.client.login(
            username="worker1@example.com",
            password="testpassword"
        )

        response = self.client.post(
            reverse("admin-employee-update-template", kwargs={"pk": worker2.pk}),
            {
                "first_name": "Jayce",
                "last_name": "Arcane",
                "phone_number": "+48765432109",
                "role": Employee.EmployeeRole.WORKER,
                "salary": 5000,
                "hire_date": date(2020, 1, 1)
            }
        )

        self.assertEqual(response.status_code, 403)

        worker2.refresh_from_db()

        self.assertEqual(worker2.first_name, "Jack")
        self.assertEqual(worker2.last_name, "Reacher")
        self.assertEqual(worker2.phone_number, "+48123456789")

    
    def test_admin_employee_can_update_employee_employment_status(self):
        self.create_employee_admin("jack.reacher@example.com")

        worker = self.create_employee_worker("worker1@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.post(
            reverse("admin-employee-employment-status-update-template", kwargs={"pk": worker.pk}),
            {
                "employment_status": Employee.EmploymentStatus.INACTIVE,
                "layoff_date": date(2024, 1, 1)
            }
        )
        
        self.assertRedirects(
            response,
            reverse("employee-list-template")
        )

        worker.refresh_from_db()

        self.assertEqual(worker.employment_status, Employee.EmploymentStatus.INACTIVE)
        self.assertEqual(worker.layoff_date, date(2024, 1, 1))


    def test_not_admin_employee_cannot_update_employee_employment_status(self):
        worker1 = self.create_employee_worker("worker1@example.com")
        worker2 = self.create_employee_worker("worker2@example.com")
        
        self.client.force_login(worker1.user)
        
        response = self.client.post(
            reverse("admin-employee-employment-status-update-template", kwargs={"pk": worker2.pk}),
            {
                "employment_status": Employee.EmploymentStatus.INACTIVE,
                "layoff_date": date(2024, 1, 1)
            }
        )

        self.assertEqual(response.status_code, 403)

        worker2.refresh_from_db()

        self.assertEqual(worker2.employment_status, Employee.EmploymentStatus.ACTIVE)

    
    def test_admin_employee_can_register_new_employee(self):
        self.create_employee_admin("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )
        
        response = self.client.post(
            reverse("admin-employee-registration-template"),
            {
                "first_name": "Jayce",
                "last_name": "Arcane",
                "email": "jayce123.arcane@example.com",
                "phone_number": "+48765432109",
                "role": Employee.EmployeeRole.WORKER,
                "salary": 5000,
                "hire_date": date(2020, 1, 1),
                "password": "testpassword"
            }
        )

        self.assertRedirects(
            response,
            reverse("employee-list-template")
        )

        self.assertTrue(
            Employee.objects.filter(
                email="jayce123.arcane@example.com"
            ).exists()
        )


    def test_customer_cannot_register_new_employee(self):
        self.create_customer("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )
        
        response = self.client.post(
            reverse("admin-employee-registration-template"),
            {
                "first_name": "Jayce",
                "last_name": "Arcane",
                "email": "jayce123.arcane@example.com",
                "phone_number": "+48765432109",
                "role": Employee.EmployeeRole.WORKER,
                "salary": 5000,
                "hire_date": date(2020, 1, 1),
                "password": "testpassword"
            }
        )

        self.assertEqual(response.status_code, 403)

        self.assertFalse(
            Employee.objects.filter(
                email="jayce123.arcane@example.com"
            ).exists()
        )

     
    def test_not_admin_employee_cannot_register_new_employee(self):
        worker = self.create_employee_worker("worker1@example.com")

        self.client.force_login(worker.user)

        response = self.client.post(
            reverse("admin-employee-registration-template"),
            {
                "first_name": "Jayce",
                "last_name": "Arcane",
                "email": "jayce123.arcane@example.com",
                "phone_number": "+48765432109",
                "role": Employee.EmployeeRole.WORKER,
                "salary": 5000,
                "hire_date": date(2020, 1, 1),
                "password": "testpassword"
            }
        )

        self.assertEqual(response.status_code, 403)

        self.assertFalse(
            Employee.objects.filter(
                email="jayce123.arcane@example.com"
            ).exists()
        )


    def test_anonymous_user_cannot_access_logout_view(self):
        response = self.client.get(reverse("logout"))

        self.assertRedirects(
            response,
            f"{reverse('login-form')}?next={reverse('logout')}"
        )


    def test_authenticated_user_can_logout(self):
        self.create_customer("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.post(
            reverse("logout"),
        )

        self.assertRedirects(
            response,
            reverse("login-form")
        )

    
    def test_inactive_employee_cannot_login(self):
        employee = self.create_employee_worker("jack.reacher@example.com")
        employee.employment_status = Employee.EmploymentStatus.INACTIVE
        employee.layoff_date = date(2024, 1, 1)
        employee.save()
        response = self.client.post(
            reverse("login-form"),
            {
                "email": "jack.reacher@example.com",
                "password": "testpassword"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your employee account is inactive.")
        self.assertTemplateUsed(response, "person/login.html")


    def test_employee_can_access_customer_list(self):
        self.create_employee_worker("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.get(
            reverse("customer-list-template")
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_employee_can_access_customer_list(self):
        self.create_employee_admin("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.get(
            reverse("customer-list-template")
        )

        self.assertEqual(response.status_code, 200)

    def test_superuser_can_access_customer_list(self):
        self.create_superuser("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.get(
            reverse("customer-list-template")
        )

        self.assertEqual(response.status_code, 200)
    
    def test_anonymous_user_cannot_access_customer_list(self):
        response = self.client.get(
            reverse("customer-list-template")
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login-form')}?next={reverse('customer-list-template')}")

    def test_customer_cannot_access_customer_list(self):
        self.create_customer("jack.reacher@example.com")

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )

        response = self.client.get(
            reverse("customer-list-template")
        )

        self.assertEqual(response.status_code, 403)

    def test_inactive_employee_cannot_access_customer_list(self):
        employee = self.create_employee_worker("jack.reacher@example.com")
        employee.employment_status = Employee.EmploymentStatus.INACTIVE
        employee.layoff_date = date(2024, 1, 1)
        employee.save()

        self.client.login(
            username="jack.reacher@example.com",
            password="testpassword"
        )
        
        response = self.client.get(
            reverse("customer-list-template")
        )

        self.assertEqual(response.status_code, 403)