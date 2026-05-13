from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Customer

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