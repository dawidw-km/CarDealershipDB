from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from cars.tests.helpers import TestHelpers
from cars.models import Car, ModerationStatus, Status
from sales.models import Sale

User = get_user_model()

class SaleTemplateViewsTestCase(TestCase, TestHelpers):

    def test_anonymous_user_cannot_access_customer_sale_registration_view(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        self.mark_car_as_approved(car)

        login_url = reverse("login-form")
        next_url = reverse("sale-car-registration-template", args=[car.id])

        response = self.client.get(next_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)

    def test_customer_cannot_access_sale_car_registration_if_car_does_not_exist(self):
        customer = self.create_customer("customer@example.com")

        self.client.login(
            username="customer@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse(
            "sale-car-registration-template",
            args=[999]),
            )

        self.assertEqual(response.status_code, 404)

    def test_customer_cannot_access_sale_car_registration_if_car_is_reserved_by_someone_else(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        reserver = self.create_customer("reserver@example.com")
        self.mark_car_as_reserved(car, reserver)
        new_buyer = self.create_customer("new_buyer@example.com")

        self.client.login(
            username="new_buyer@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse(
            "sale-car-registration-template",
            args=[car.id]),
            )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.RESERVED)
        self.assertEqual(car.buyer, reserver)

    def test_customer_cannot_access_sale_car_registration_if_car_is_alredy_sold(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        self.mark_car_as_sold(car, buyer)
        new_buyer = self.create_customer("new_buyer@example.com")

        self.client.login(
            username="new_buyer@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse(
            "sale-car-registration-template",
            args=[car.id]),
            )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, buyer)

    def test_customer_cannot_access_sale_car_registration_if_car_is_not_approved(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        buyer = self.create_customer("buyer@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse(
            "sale-car-registration-template",
            args=[car.id]),
            )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)

    def test_owner_cannot_buy_his_own_car(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)

        self.client.login(
            username="owner@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse(
            "sale-car-registration-template",
            args=[car.id]),
            )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)
        self.assertEqual(car.buyer, None)

    def test_customer_can_buy_a_car(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
            )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customer-profile"))
        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, buyer)
    
    def test_employee_cannot_buy_a_car(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)

        self.client.login(
            username="employee@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse(
            "sale-car-registration-template",
            args=[car.id]),
            )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)
        self.assertEqual(car.buyer, None)

    def test_superuser_cannot_buy_a_car(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        superuser = self.create_superuser("superuser@example.com")

        self.client.login(
            username="superuser@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse(
            "sale-car-registration-template",
            args=[car.id]),
            )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)
        self.assertEqual(car.buyer, None)

    def test_buyer_can_view_his_transactions(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
        )
        
        self.assertRedirects(response, reverse("customer-profile"))

        sale = Sale.objects.get(buyer=buyer, car=car)

        response = self.client.get(reverse("buyer-sales-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sales/sale_list.html")
        self.assertContains(response, owner.first_name)
        self.assertContains(response, buyer.first_name)
        self.assertContains(response, "My Transactions")
        self.assertContains(response, sale.transaction_number)

    def test_owner_can_view_his_transactions(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
     

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
        )
        
        self.assertRedirects(response, reverse("customer-profile"))

        sale = Sale.objects.get(buyer=buyer, car=car)

        self.client.login(
            username="owner@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse("owner-sales-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sales/sale_list.html")
        self.assertContains(response, owner.first_name)
        self.assertContains(response, buyer.first_name)
        self.assertContains(response, "My Transactions")
        self.assertContains(response, sale.transaction_number)

    def test_employee_can_view_transactions(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
        )
        
        self.assertRedirects(response, reverse("customer-profile"))
        
        sale = Sale.objects.get()

        self.client.login(
            username="employee@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse("staff-sales-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sales/sale_list.html")
        self.assertContains(response, owner.first_name)
        self.assertContains(response, buyer.first_name)
        self.assertContains(response, "Transactions")
        self.assertContains(response, sale.transaction_number)

    def test_superuser_can_view_transactions(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        superuser = self.create_superuser("superuser@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
        )
        
        self.assertRedirects(response, reverse("customer-profile"))
        
        sale = Sale.objects.get()

        self.client.login(
            username="superuser@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse("staff-sales-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, sale.transaction_number)

    def test_anonymous_user_cannot_access_buyer_sales_list_view(self):
        login_url = reverse("login-form")
        next_url = reverse("buyer-sales-list-template")

        response = self.client.get(reverse("buyer-sales-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)

    def test_anonymous_user_cannot_access_owner_sales_list_view(self):
        login_url = reverse("login-form")
        next_url = reverse("owner-sales-list-template")

        response = self.client.get(reverse("owner-sales-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)

    def test_anonymous_user_cannot_access_staff_sales_list_view(self):
        login_url = reverse("login-form")
        next_url = reverse("staff-sales-list-template")

        response = self.client.get(reverse("staff-sales-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)

    def test_user_cannot_access_buyer_sales_list_view(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        user = self.create_customer("user@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
        )

        self.assertRedirects(response, reverse("customer-profile"))

        self.client.login(
            username="user@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse("buyer-sales-list-template"))

        self.assertEqual(response.status_code, 302)

    def test_user_cannot_access_owner_sales_list_view(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        user = self.create_customer("user@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
        )

        self.client.login(
            username="user@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse("owner-sales-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customer-profile"))
        
    def test_user_cannot_access_staff_sales_list_view(self):
        owner = self.create_customer("owner@example.com")
        car = self.create_car(owner=owner)
        employee = self.create_employee_worker("employee@example.com")
        self.mark_car_as_approved(car, employee)
        buyer = self.create_customer("buyer@example.com")
        user = self.create_customer("user@example.com")

        self.client.login(
            username="buyer@example.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("sale-car-registration-template",
            args=[car.id]),
            {"payment_method": Sale.PaymentMethod.CARD}
        )

        self.assertRedirects(response, reverse("customer-profile"))

        self.client.login(
            username="user@example.com",
            password="testpass123"
        )

        response = self.client.get(reverse("staff-sales-list-template"))

        self.assertEqual(response.status_code, 403)