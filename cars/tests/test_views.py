from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Car, Status, ModerationStatus
from person.models import Customer, Employee
from datetime import date
from rest_framework import status

User = get_user_model()

class CarViewsTestCase(APITestCase):

    # Helper methods to create test data

    def create_user(self, email):
        return User.objects.create_user(
            username=email,
            email=email,
            password="testpass123"
        )
    
    def create_superuser(self, email):
        return User.objects.create_superuser(
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

    def create_car(self, owner=None):
        if owner is None:
            owner = self.create_customer("unique_owner@gmail.com")
        return Car.objects.create(
            owner=owner,
            brand="Toyota",
            model="Corolla",
            color="Red",
            vehicle_type="sedan",
            year=2020,
            vin="1HGCM82633A004352",
            mileage=100,
            fuel_type="gasoline",
            transmission="manual",
            vehicle_condition="new",
            accident_status="accident_free",
            listing_price=10000,
            description="This is a new car",
        )

    def get_valid_car_data(self):
        return {
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Red",
            "vehicle_type": "sedan",
            "year": 2020,
            "vin": "1HGCM82633A004352",
            "mileage": 100,
            "fuel_type": "gasoline",
            "transmission": "manual",
            "vehicle_condition": "new",
            "accident_status": "accident_free",
            "listing_price": 10000,
            "description": "This is a new car",
        }


    # Test cases

    def test_anonymous_user_cannot_register_car(self):
        response = self.client.post(
            reverse("car-registration"),
            self.get_valid_car_data(),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_update_car(self):
        data = {
            "brand": "BMW"
        }

        car = self.create_car()

        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_anonymous_user_cannot_soft_delete_car(self):
        car = self.create_car()
        response = self.client.put(
            reverse("car-soft-delete", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_anonymous_user_cannot_change_moderation_status_to_approved(self):
        car = self.create_car()
        response = self.client.put(
            reverse("car-moderation-status-update-approved", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_change_moderation_status_to_rejected(self):
        car = self.create_car()
        response = self.client.put(
            reverse("car-moderation-status-update-rejected", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_change_purchase_status_to_sold(self):
        car = self.create_car()
        response = self.client.put(
            reverse("car-purchase-status-update-sold", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_change_purchase_status_to_reserved(self):
        car = self.create_car()
        response = self.client.put(
            reverse("car-purchase-status-update-reserved", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_can_add_new_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        response = self.client.post(
            reverse("car-registration"),
            self.get_valid_car_data(),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], customer.id)

    def test_customer_can_update_own_car(self):
        data = {
            "brand": "BMW"
        }
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.brand, "BMW")
        self.assertEqual(car.owner, customer)

    def test_customer_cannot_update_other_customer_car(self):
        data = {
            "brand": "BMW"
        }
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_not_owner = self.create_customer("testuser2@gmail.com")

        car = self.create_car(owner=customer_owner)

        self.client.force_authenticate(user=customer_not_owner.user)
        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.brand, "Toyota")
        self.assertEqual(car.owner, customer_owner)

    def test_customer_can_soft_delete_own_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.put(
            reverse("car-soft-delete", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, True)

    def test_customer_cannot_soft_delete_other_customer_car(self):
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_not_owner = self.create_customer("testuser2@gmail.com")

        car = self.create_car(owner=customer_owner)

        self.client.force_authenticate(user=customer_not_owner.user)
        response = self.client.put(
            reverse("car-soft-delete", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)

    def test_customer_cannot_change_moderation_status_to_approved(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.put(
            reverse("car-moderation-status-update-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

    def test_customer_cannot_change_moderation_status_to_rejected(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.put(
            reverse("car-moderation-status-update-rejected", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

    def test_customer_owner_cannot_change_status_to_sold(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.put(
            reverse("car-purchase-status-update-sold", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)

    def test_customer_owner_cannot_change_status_to_reserved(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.put(
            reverse("car-purchase-status-update-reserved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)

    def test_customer_non_owner_cannot_change_moderation_status_to_approved_someone_elses_car(self):
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_not_owner = self.create_customer("testuser2@gmail.com")

        car = self.create_car(owner=customer_owner)

        self.client.force_authenticate(user=customer_not_owner.user)
        response = self.client.put(
            reverse("car-moderation-status-update-approved", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

    def test_customer_non_owner_can_change_status_to_sold_someone_elses_car(self):
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_not_owner = self.create_customer("testuser2@gmail.com")
        employee = self.create_employee_worker("testuser3@gmail.com")

        car = self.create_car(owner=customer_owner)

        car.moderation_status = ModerationStatus.APPROVED
        car.reviewer = employee
        car.save()

        self.client.force_authenticate(user=customer_not_owner.user)
        response = self.client.put(
            reverse("car-purchase-status-update-sold", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, customer_not_owner)

    def test_customer_non_owner_can_change_status_to_reserved_someone_elses_car(self):
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_not_owner = self.create_customer("testuser2@gmail.com")
        employee = self.create_employee_worker("testuser3@gmail.com")
        car = self.create_car(owner=customer_owner)

        car.moderation_status = ModerationStatus.APPROVED
        car.reviewer = employee
        car.save()

        self.client.force_authenticate(user=customer_not_owner.user)
        response = self.client.put(
            reverse("car-purchase-status-update-reserved", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.RESERVED)
        self.assertEqual(car.buyer, customer_not_owner)
    
    def test_customer_who_reserved_car_can_change_status_to_sold(self):
        customer = self.create_customer("testuser1@gmail.com")
        customer_buyer = self.create_customer("testuser2@gmail.com")
        employee = self.create_employee_worker("testuser3@gmail.com")
        car = self.create_car(owner=customer)

        car.moderation_status = ModerationStatus.APPROVED
        car.reviewer = employee
        car.save()

        car.status = Status.RESERVED
        car.buyer = customer_buyer
        car.save()

        self.client.force_authenticate(user=customer_buyer.user)
        response = self.client.put(
            reverse("car-purchase-status-update-sold", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, customer_buyer)

    def test_different_customer_cannot_change_status_to_sold_to_reserved_car_by_someone_else(self):
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_buyer = self.create_customer("testuser2@gmail.com")
        customer_reserver = self.create_customer("testuser3@gmail.com")
        employee = self.create_employee_worker("testuser4@gmail.com")
        car = self.create_car(owner=customer_owner)

        car.moderation_status = ModerationStatus.APPROVED
        car.reviewer = employee
        car.save()

        car.status = Status.RESERVED
        car.buyer = customer_reserver
        car.save()

        self.client.force_authenticate(user=customer_buyer.user)
        response = self.client.put(
            reverse("car-purchase-status-update-sold", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.RESERVED)
        self.assertEqual(car.buyer, customer_reserver)

    def test_not_approved_car_cannot_be_reserved(self):
        customer = self.create_customer("testuser1@gmail.com")
        customer_reserver = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)

        self.client.force_authenticate(user=customer_reserver.user)
        response = self.client.put(
            reverse("car-purchase-status-update-reserved", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)
        self.assertEqual(car.buyer, None)

    def test_not_approved_car_cannot_be_sold(self):
        customer = self.create_customer("testuser1@gmail.com")
        customer_buyer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)

        self.client.force_authenticate(user=customer_buyer.user)
        response = self.client.put(
            reverse("car-purchase-status-update-sold", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.AVAILABLE)
        self.assertEqual(car.buyer, None)

    def test_employee_can_view_all_cars(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        car = self.create_car(owner=customer)

        self.client.force_authenticate(user=employee.user)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_owner_or_employee_cannot_view_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        viewer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)

        self.client.force_authenticate(user=viewer.user)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_view_all_cars(self):
        superuser = self.create_superuser("testuser1@gmail.com")
        customer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        self.client.force_authenticate(user=superuser)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_view_own_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_cannot_view_other_customer_car(self):
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_not_owner = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer_owner)

        self.client.force_authenticate(user=customer_not_owner.user)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_view_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_for_viewer_car_detail_returns_404_for_deleted_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        viewer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        car.is_deleted = True
        car.save()
        self.client.force_authenticate(user=viewer.user)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_for_owner_car_detail_returns_404_for_deleted_car(self):
        owner = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=owner)
        car.is_deleted = True
        car.save()
        self.client.force_authenticate(user=owner.user)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_for_employee_car_detail_returns_404_for_deleted_car(self):
        owner = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        car = self.create_car(owner=owner)
        car.is_deleted = True
        car.save()
        self.client.force_authenticate(user=employee.user)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_for_superuser_car_detail_returns_404_for_deleted_car(self):
        superuser = self.create_superuser("testuser1@gmail.com")
        car = self.create_car()
        car.is_deleted = True
        car.save()
        self.client.force_authenticate(user=superuser)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_car_detail_returns_404_for_non_existent_car(self):
        viewer = self.create_customer("testuser2@gmail.com")
        self.client.force_authenticate(user=viewer.user)
        response = self.client.get(
            reverse("car-detail", args=[999999]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_inactive_employee_cannot_view_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        employee.employment_status = Employee.EmploymentStatus.INACTIVE
        employee.layoff_date = date(2024, 1, 1)
        employee.save()
        car = self.create_car(owner=customer)
        self.client.force_authenticate(user=employee.user)
        response = self.client.get(
            reverse("car-detail", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)