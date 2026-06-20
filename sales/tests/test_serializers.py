from django.test import TestCase
from rest_framework.exceptions import ValidationError
from ..serializers import SaleRegistrationSerializer
from cars.tests.helpers import TestHelpers
from sales.models import Sale
from cars.models import Status

class SaleSerializerTestCase(TestCase, TestHelpers):

    def test_create_sale_serializer_is_valid(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        buyer = self.create_customer("customer@example.com")
        request = self.request_with_user(buyer.user)
        car = self.mark_car_as_approved(car)

        serializer = SaleRegistrationSerializer(
            data={"payment_method": Sale.PaymentMethod.CARD},
            context={
                "request": request,
                "car": car
            }
        )

        self.assertTrue(serializer.is_valid())
        sale = serializer.save()
        self.assertEqual(sale.seller, car.owner)
        self.assertEqual(sale.buyer, buyer)
        self.assertEqual(sale.car, car)
        self.assertEqual(sale.sale_price, car.listing_price)
        self.assertEqual(sale.payment_method, Sale.PaymentMethod.CARD)

    def test_create_sale_serializer_no_payment_method(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        buyer = self.create_customer("buyer@example.com")
        request = self.request_with_user(buyer.user)

        serializer = SaleRegistrationSerializer(
            data={},
            context={
                "request": request,
                "car": car
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_create_sale_with_no_customer_profile(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        buyer = self.create_employee_worker("buyer_worker@example.com")
        request = self.request_with_user(buyer.user)

        serializer = SaleRegistrationSerializer(
            data={"payment_method": Sale.PaymentMethod.CARD},
            context={
                "request": request,
                "car": car
            }
        )
        
        serializer.is_valid()
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_ensure_car_status_and_buyer_are_updated(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner)
        buyer = self.create_customer("buyer@example.com")
        employee = self.create_employee_worker("employee@example.com")
        car = self.mark_car_as_approved(car, employee)

        request = self.request_with_user(buyer.user)

        serializer = SaleRegistrationSerializer(
            data={"payment_method": Sale.PaymentMethod.CARD},
            context={
                "request": request,
                "car": car
            }
        )

        serializer.is_valid()
        sale = serializer.save()

        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, buyer)
        self.assertEqual(sale.seller, car.owner)
        self.assertEqual(sale.buyer, buyer)
        self.assertEqual(sale.car, car)
        