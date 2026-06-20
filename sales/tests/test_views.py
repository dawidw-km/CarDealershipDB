from rest_framework.test import APITestCase
from django.urls import reverse
from cars.tests.helpers import TestHelpers
from sales.models import Sale
from cars.models import Status
from rest_framework import status

class SaleViewsTestCase(APITestCase, TestHelpers):

    # Test cases

    def test_anonymous_user_cannot_register_sale(self):
        car = self.create_car()

        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_buyer_can_register_sale(self):
        owner = self.create_customer("customer@example.com")
        car = self.create_car(owner)
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")

        self.client.force_authenticate(user=buyer.user)

        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(Sale.objects.first().buyer, buyer)
        self.assertEqual(Sale.objects.first().car, car)
        self.assertEqual(Sale.objects.first().payment_method, Sale.PaymentMethod.CARD)

    def test_employee_cannot_register_sale(self):
        owner = self.create_customer("customer@example.com")
        car = self.create_car(owner)
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)

        self.client.force_authenticate(user=employee.user)

        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_cannot_register_sale(self):
        owner = self.create_customer("customer@example.com")
        car = self.create_car(owner)
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)
        superuser = self.create_superuser("superuser@example.com")

        self.client.force_authenticate(user=superuser)

        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_buyer_cannot_register_sale_for_not_approved_car(self):
        owner = self.create_customer("customer@example.com")
        car = self.create_car(owner)
        buyer = self.create_customer("buyer@example.com")

        self.client.force_authenticate(user=buyer.user)

        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Car is not approved.", str(response.data))
    
    def test_owner_cannot_buy_their_own_car(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)
        
        self.client.force_authenticate(user=owner.user)
        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Sale.objects.count(), 0)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)
        self.assertEqual(car.buyer, None)

    def test_second_buyer_cannot_register_sale_for_the_same_car(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        buyer_2 = self.create_customer("buyer2@example.com")
        
        self.client.force_authenticate(user=buyer.user)
        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(Sale.objects.first().buyer, buyer)
        self.assertEqual(Sale.objects.first().car, car)
        self.assertEqual(Sale.objects.first().payment_method, Sale.PaymentMethod.CARD)

        self.client.force_authenticate(user=buyer_2.user)
        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Sold cars cannot be purchased.", str(response.data))
        self.assertEqual(Sale.objects.count(), 1)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, buyer)

    def test_buyer_can_buy_a_car_that_was_reserved_by_himself(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        car = self.mark_car_as_reserved(car, buyer)
        
        self.client.force_authenticate(user=buyer.user)
        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sale.objects.count(), 1)
        self.assertEqual(Sale.objects.first().buyer, buyer)
        self.assertEqual(Sale.objects.first().car, car)
        self.assertEqual(Sale.objects.first().payment_method, Sale.PaymentMethod.CARD)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, buyer)

    def test_buyer_cannot_buy_a_car_that_was_reserved_by_someone_else(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        car = self.mark_car_as_reserved(car, buyer)
        buyer_2 = self.create_customer("buyer2@example.com")
        
        self.client.force_authenticate(user=buyer_2.user)
        response = self.client.post(
            reverse("sale-car-registration", args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You are not authorized to purchase this car.", str(response.data))
        self.assertEqual(Sale.objects.count(), 0)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.RESERVED)
        self.assertEqual(car.buyer, buyer)