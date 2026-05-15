from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Customer, Employee

User = get_user_model()


class CustomerTemplateViewsTestCase(TestCase):

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
            hire_date=date(2020, 1, 1)
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
            "/login/customer/form/?next=/customer/profile/update/"
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
            reverse("customer-login-form")
        )
    
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

        self.assertEqual(response.context["error"], "Wrong password.")

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
            "/login/customer/form/?next=/user/change-password/"
        )
    
    def test_employee_can_access_employee_profile(self):
        employee = self.create_employee_worker("jack.reacher@example.com")

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