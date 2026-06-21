from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .helpers import TestHelpers
from cars.models import Car, ModerationStatus, Status

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

    def test_owner_can_access_owner_cars_list_view(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("owner-cars-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/owner_cars_list.html")
        self.assertContains(response, car.brand)
        self.assertContains(response, car.model)

    def test_owner_is_redirected_to_customer_profile_if_no_cars(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("owner-cars-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customer-profile"))

    def test_employee_cannot_access_owner_cars_list_view(self):
        employee = self.create_employee_worker("testuser1@gmail.com")

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("owner-cars-list-template"))

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_access_owner_cars_list_view(self):
        login_url = reverse("login-form")
        next_url = reverse("owner-cars-list-template")

        response = self.client.get(next_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)

    def test_employee_can_access_employee_admin_deleted_cars_list_view(self):
        customer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        self.mark_car_as_deleted(car)

        employee_admin = self.create_employee_admin("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("employee-deleted-cars-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/employee_deleted_cars_list.html")
        self.assertContains(response, car.brand)
        self.assertContains(response, car.model)

    def test_employee_is_redirected_to_employee_profile_if_no_deleted_cars(self):
        employee_admin = self.create_employee_admin("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("employee-deleted-cars-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("employee-profile"))

    def test_employee_worker_is_redirected_to_employee_profile_if_no_deleted_cars(self):
        employee_worker = self.create_employee_worker("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.get(reverse("employee-deleted-cars-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("employee-profile"))

    def test_employee_worker_can_access_employee_deleted_cars_list_view(self):
        customer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        self.mark_car_as_deleted(car)

        employee_worker = self.create_employee_worker("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("employee-deleted-cars-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/employee_deleted_cars_list.html")
        self.assertContains(response, car.brand)
        self.assertContains(response, car.model)

    def test_anonymous_user_cannot_access_employee_deleted_cars_list_view(self):
        login_url = reverse("login-form")
        next_url = reverse("employee-deleted-cars-list-template")

        response = self.client.get(next_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)
    
    def test_superuser_can_access_employee_deleted_cars_list_view(self):
        customer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        self.mark_car_as_deleted(car)

        superuser = self.create_superuser("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("employee-deleted-cars-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/employee_deleted_cars_list.html")
        self.assertContains(response, car.brand)
        self.assertContains(response, car.model)
    
    def test_superuser_is_redirected_to_employee_profile_if_no_deleted_cars(self):
        superuser = self.create_superuser("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("employee-deleted-cars-list-template"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("employee-profile"))

    def test_customer_cannot_access_employee_deleted_cars_list_view(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.get(reverse("employee-deleted-cars-list-template"))

        self.assertEqual(response.status_code, 403)

    def test_employee_can_access_employee_car_moderation_list_view(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        employee_worker = self.create_employee_worker("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.get(reverse("employee-car-moderation-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/employee_car_moderation_list.html")

    def test_non_employee_cannot_access_employee_car_moderation_list_view(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.get(reverse("employee-car-moderation-list-template"))

        self.assertEqual(response.status_code, 403)
    
    def test_anonymous_user_cannot_access_employee_car_moderation_list_view(self):
        login_url = reverse("login-form")
        next_url = reverse("employee-car-moderation-list-template")

        response = self.client.get(next_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)

    def test_superuser_can_access_employee_car_moderation_list_view(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.get(reverse("employee-car-moderation-list-template"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/employee_car_moderation_list.html")\

    def test_employee_can_change_moderation_status_to_approved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        employee_worker = self.create_employee_worker("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-moderation-update-approved-template",
            args=[car.id]),
            )
        self.assertRedirects(response, reverse("employee-car-moderation-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertEqual(car.reviewer, employee_worker)

    def test_employee_can_change_moderation_status_to_rejected(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        employee_worker = self.create_employee_worker("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse(
                "employee-car-moderation-update-rejected-template",
                args=[car.id]),
            )
        self.assertRedirects(response, reverse("employee-car-moderation-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.REJECTED)
        self.assertEqual(car.reviewer, employee_worker)

    def test_admin_employee_can_change_moderation_status_to_approved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        admin_employee = self.create_employee_admin("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-moderation-update-approved-template", args=[car.id]),
        )
        self.assertRedirects(response, reverse("employee-car-moderation-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertEqual(car.reviewer, admin_employee)

    def test_admin_employee_can_change_moderation_status_to_rejected(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        admin_employee = self.create_employee_admin("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-moderation-update-rejected-template", args=[car.id]),
        )
        self.assertRedirects(response, reverse("employee-car-moderation-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.REJECTED)
        self.assertEqual(car.reviewer, admin_employee)
        
    def test_anonymous_user_cannot_change_moderation_status_to_approved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        login_url = reverse("login-form")
        next_url = reverse("employee-car-moderation-update-approved-template", args=[car.id])

        response = self.client.post(
            reverse("employee-car-moderation-update-approved-template", args=[car.id]),
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)
        
    def test_anonymous_user_cannot_change_moderation_status_to_rejected(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        login_url = reverse("login-form")
        next_url = reverse("employee-car-moderation-update-rejected-template", args=[car.id])

        response = self.client.post(
            reverse("employee-car-moderation-update-rejected-template", args=[car.id]),
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, login_url+"?next="+next_url)
        
    def test_superuser_cannot_change_moderation_status_to_approved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-moderation-update-approved-template", args=[car.id]),
        )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)
    
    def test_superuser_cannot_change_moderation_status_to_rejected(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-moderation-update-rejected-template", args=[car.id]),
        )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

    def test_owner_can_access_owner_car_update_view(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        
        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.get(
            reverse("owner-car-update-template",
            args=[car.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars/owner_car_update.html")
        self.assertContains(response, car.brand)
        self.assertContains(response, car.model)

    def test_owner_can_update_own_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        self.mark_car_as_approved(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "brand": "BMW",
                "model": "X5",
                "color": "Red",
            }
        )
        self.assertRedirects(response, reverse("owner-cars-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.brand, "BMW")
        self.assertEqual(car.model, "X5")
        self.assertEqual(car.color, "Red")

    def test_owner_cannot_update_own_car_with_invalid_data(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car.vin = "1HGCM82633A004353"
        car.save()
        self.mark_car_as_approved(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "vin": "invalid_vin",
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid VIN format.")
        car.refresh_from_db()
        self.assertEqual(car.vin, "1HGCM82633A004353")

    def test_moderation_status_is_updated_to_pending_if_owner_updates_critical_fields_of_own_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        self.mark_car_as_approved(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "brand": "Mercedes",
            }
        )

        self.assertRedirects(response, reverse("owner-cars-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

    def test_moderation_status_is_not_updated_if_owner_updates_non_critical_fields_of_own_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        self.mark_car_as_approved(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "description": "This is a new car",
            }
        )
        self.assertRedirects(response, reverse("owner-cars-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.description, "This is a new car")
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertFalse(car.reviewer is None)
        
    def test_owner_cannot_update_own_car_that_is_reserved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_reserved(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "brand": "Mercedes",
                "model": "C-Class",
            }
        )

        self.assertRedirects(response, reverse("owner-cars-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.model, "Corolla")
        self.assertEqual(car.status, Status.RESERVED)
        self.assertTrue(car.buyer is not None)
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)

    def test_owner_cannot_update_own_car_that_is_sold(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_sold(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "brand": "Mercedes",
                "model": "C-Class",
            }
        )
        self.assertRedirects(response, reverse("owner-cars-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.model, "Corolla")
        self.assertEqual(car.status, Status.SOLD)
        self.assertTrue(car.buyer is not None)
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)

    def test_employee_cannot_update_a_car_that_belongs_to_owner(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)

        employee = self.create_employee_worker("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "brand": "Mercedes",
                "model": "C-Class",
            }
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.model, "Corolla")
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)

    def test_superuser_cannot_update_a_car_that_belongs_to_owner(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)

        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("owner-car-update-template",
            args=[car.id]),
            {
                "brand": "Mercedes",
                "model": "C-Class",
            }
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.model, "Corolla")
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)

    def test_employee_cannot_soft_delete_a_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)

        employee = self.create_employee_worker("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)

    def test_superuser_can_soft_delete_a_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)

        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )
        self.assertRedirects(response, reverse("public-car-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, True)
    
    def test_owner_can_soft_delete_a_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car_2 = Car.objects.create(
            owner=customer,
            brand="Toyota",
            model="Corolla",
            color="Red",
            vehicle_type="sedan",
            year=2020,
            vin="1HGCM82633A004353",
            mileage=100,
            fuel_type="gasoline",
            transmission="manual",
            vehicle_condition="new",
            accident_status="accident_free",
            listing_price=10000,
            description="This is a new car",
        )
        car = self.mark_car_as_approved(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )

        response = self.client.post(
            reverse("customer-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )

        self.assertRedirects(response, reverse("owner-cars-list-template"))
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, True)

    def test_owner_cannot_soft_delete_a_car_that_is_reserved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_reserved(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        
        response = self.client.post(
            reverse("customer-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )

        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)
        self.assertEqual(car.status, Status.RESERVED)
        self.assertTrue(car.buyer is not None)
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)

    def test_owner_cannot_soft_delete_a_car_that_is_sold(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_sold(car)

        self.client.login(
            username="testuser1@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("customer-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)
        self.assertEqual(car.status, Status.SOLD)
        self.assertTrue(car.buyer is not None)
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)

    def test_employee_cannot_soft_delete_a_car_that_is_sold(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_sold(car)

        employee = self.create_employee_worker("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)
        self.assertEqual(car.status, Status.SOLD)

    def test_employee_cannot_soft_delete_a_car_that_is_reserved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_reserved(car)

        employee = self.create_employee_worker("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)
        self.assertEqual(car.status, Status.RESERVED)
        self.assertTrue(car.buyer is not None)
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)


    def test_superuser_cannot_soft_delete_a_car_that_is_reserved(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_reserved(car)

        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)
        self.assertEqual(car.status, Status.RESERVED)
        self.assertTrue(car.buyer is not None)
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)

    def test_superuser_cannot_soft_delete_a_car_that_is_sold(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_sold(car)

        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.login(
            username="testuser2@gmail.com",
            password="testpass123"
        )
        response = self.client.post(
            reverse("employee-car-action-update-softdelete-template",
            args=[car.id]),
            {}
        )
        self.assertEqual(response.status_code, 403)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)
        self.assertEqual(car.status, Status.SOLD)
        self.assertTrue(car.buyer is not None)
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertTrue(car.reviewer is not None)

    def test_anonymous_user_cannot_soft_delete_a_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)

        login_url = reverse("login-form")
        next_url = reverse("customer-car-action-update-softdelete-template", args=[car.id])

        response = self.client.post(
            reverse("customer-car-action-update-softdelete-template", args=[car.id]),
            {}
        )
        self.assertRedirects(response,
        login_url+"?next="+next_url
        )