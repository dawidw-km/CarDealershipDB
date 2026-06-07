from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .helpers import TestHelpers
from cars.models import Car

User = get_user_model()

class CarTemplateViewsTestCase(TestCase, TestHelpers):

    def test_customer_car_register_a_new_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.post(reverse("customer-car-registration-template"), {
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": "12345678901234567",
            "mileage": 100,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "new",
            "accident_status": "accident_free",
            "listing_price": 10000.00,
            "description": "This is a new car",
        })

        self.assertRedirects(response, reverse("customer-profile"))
        self.assertTrue(Car.objects.filter(owner=customer).exists())
        self.assertTrue(Car.objects.filter(brand="Toyota", model="Corolla").exists())

    def test_customer_cannot_register_a_new_car_with_invalid_data(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.post(reverse("customer-car-registration-template"), {
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 5000,
            "vin": "12345678901234567",
            "mileage": 100,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "new",
            "accident_status": "accident_free",
            "listing_price": 10000.00,
            "description": "This is a new car",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Date of production cannot be in the future.")

    def test_employee_cannot_register_a_new_car(self):
        employee = self.create_employee_worker("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.post(reverse("customer-car-registration-template"), {
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": "12345678901234567",
            "mileage": 100,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "new",
            "accident_status": "accident_free",
            "listing_price": 10000,
            "description": "This is a new car",
        })

        self.assertEqual(response.status_code, 403)

        self.assertFalse(Car.objects.filter(brand="Toyota", model="Corolla").exists())

    def test_anonymous_user_cannot_register_a_new_car(self):
        login_url = reverse("login-form")
        next_url = reverse("customer-car-registration-template")

        response = self.client.post(next_url, {
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)
    
    def test_customer_can_access_customer_car_registration_view(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.get(reverse("customer-car-registration-template"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/customer_car_registration.html")
    
    def test_vin_cannot_be_used_by_another_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        car = self.create_car(owner=customer)
        car.vin = "1234WQ78901234567"
        car.save()

        response = self.client.post(reverse("customer-car-registration-template"), {
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": "1234WQ78901234567",
            "mileage": 100,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "new",
            "accident_status": "accident_free",
            "listing_price": 10000.00,
            "description": "This is a new car",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "car with this vin already exists.")
        self.assertEqual(Car.objects.filter(vin="1234WQ78901234567").count(), 1)


    def test_public_car_list_view(self):

        customer = self.create_customer("testuser1@gmail.com")

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        car = self.create_car(owner=customer)
        self.mark_car_as_approved(car)

        response = self.client.get(reverse("public-car-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/public_cars_list.html")
        self.assertContains(response, car.brand)
        self.assertContains(response, car.model)

    def test_anonymous_user_can_access_public_car_list_view(self):
        car = self.create_car()
        self.mark_car_as_approved(car)

        response = self.client.get(reverse("public-car-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/public_cars_list.html")
        self.assertContains(response, car.brand)
        self.assertContains(response, car.model)

    def test_public_car_list_hides_unapproved_cars(self):
        car = self.create_car()

        response = self.client.get(reverse("public-car-list-template"))

        self.assertNotContains(response, car.brand)
        self.assertNotContains(response, car.model)

    def test_public_car_list_hides_deleted_cars(self):
        car = self.create_car()
        self.mark_car_as_approved(car)
        self.mark_car_as_deleted(car)

        response = self.client.get(reverse("public-car-list-template"))

        self.assertNotContains(response, car.brand)
        self.assertNotContains(response, car.model)