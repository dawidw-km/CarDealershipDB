from rest_framework.test import APITestCase
from django.urls import reverse
from ..models import Status, ModerationStatus
from rest_framework import status
from .helpers import TestHelpers

class CarViewsTestCase(APITestCase, TestHelpers):

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

    def test_customer_non_owner_can_change_status_to_reserved_someone_elses_car(self):
        customer_owner = self.create_customer("testuser1@gmail.com")
        customer_not_owner = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer_owner)

        car = self.mark_car_as_approved(car)

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

    def test_employee_can_view_all_cars(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        car = self.create_car(owner=customer)

        self.client.force_authenticate(user=employee.user)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
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
            reverse("car-detail-not-approved", args=[car.id]),
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
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_view_own_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        self.client.force_authenticate(user=customer.user)
        car = self.create_car(owner=customer)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
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
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_view_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)

        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_for_viewer_car_detail_returns_404_for_deleted_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        viewer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_deleted(car)
        self.client.force_authenticate(user=viewer.user)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_for_owner_car_detail_returns_404_for_deleted_car(self):
        owner = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=owner)
        car = self.mark_car_as_deleted(car)
        self.client.force_authenticate(user=owner.user)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_for_employee_car_detail_returns_404_for_deleted_car(self):
        owner = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        car = self.create_car(owner=owner)
        car = self.mark_car_as_deleted(car)
        self.client.force_authenticate(user=employee.user)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_for_superuser_car_detail_returns_404_for_deleted_car(self):
        superuser = self.create_superuser("testuser1@gmail.com")
        car = self.create_car()
        car = self.mark_car_as_deleted(car)
        self.client.force_authenticate(user=superuser)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_car_detail_returns_404_for_non_existent_car(self):
        viewer = self.create_customer("testuser2@gmail.com")
        self.client.force_authenticate(user=viewer.user)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[999999]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_inactive_employee_cannot_view_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        employee = self.mark_employee_as_inactive(employee)
        car = self.create_car(owner=customer)
        self.client.force_authenticate(user=employee.user)
        response = self.client.get(
            reverse("car-detail-not-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_cannot_update_sold_car(self):
        data = {
            "brand": "BMW"
        }

        owner = self.create_customer("testuser1@gmail.com")
        buyer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=owner)

        car = self.mark_car_as_approved(car)

        car = self.mark_car_as_sold(car, buyer=buyer)

        self.client.force_authenticate(user=owner.user)
        response = self.client.put(
            reverse("car-detail-update", args=[car.id]),
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.status, Status.SOLD)
        self.assertEqual(car.buyer, buyer)
        self.assertEqual(car.brand, "Toyota")

    def test_owner_cannot_soft_delete_sold_car(self):
        owner = self.create_customer("testuser1@gmail.com")
        buyer = self.create_customer("testuser2@gmail.com")
        car = self.create_car(owner=owner)

        car = self.mark_car_as_approved(car)
        
        car = self.mark_car_as_sold(car, buyer=buyer)

        self.client.force_authenticate(user=owner.user)
        response = self.client.put(
            reverse("car-soft-delete", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)

    def test_active_employee_can_change_moderation_status_to_approved(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        car = self.create_car(owner=customer)

        self.client.force_authenticate(user=employee.user)
        response = self.client.put(
            reverse("car-moderation-status-update-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertEqual(car.reviewer, employee)

    def test_inactive_employee_cannot_change_moderation_status_to_approved(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        employee = self.mark_employee_as_inactive(employee)
        car = self.create_car(owner=customer)
        self.client.force_authenticate(user=employee.user)
        response = self.client.put(
            reverse("car-moderation-status-update-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)
    
    def test_inactive_employee_cannot_change_moderation_status_to_rejected(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        employee = self.mark_employee_as_inactive(employee)
        car = self.create_car(owner=customer)
        self.client.force_authenticate(user=employee.user)
        response = self.client.put(
            reverse("car-moderation-status-update-rejected", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)

    def test_active_employee_can_change_moderation_status_to_rejected(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_worker("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        self.client.force_authenticate(user=employee.user)
        response = self.client.put(
            reverse("car-moderation-status-update-rejected", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.REJECTED)
        self.assertEqual(car.reviewer, employee)

    def test_employee_cannot_register_car(self):
        employee = self.create_employee_worker("testuser1@gmail.com")
        self.client.force_authenticate(user=employee.user)
        response = self.client.post(
            reverse("car-registration"),
            self.get_valid_car_data(),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_cannot_register_car(self):
        superuser = self.create_superuser("testuser1@gmail.com")
        self.client.force_authenticate(user=superuser)
        response = self.client.post(
            reverse("car-registration"),
            self.get_valid_car_data(),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_can_view_approved_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        response = self.client.get(
            reverse("car-detail-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_anonymous_user_cannot_view_not_approved_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        response = self.client.get(
            reverse("car-detail-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_user_cannot_view_deleted_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_deleted(car)
        response = self.client.get(
            reverse("car-detail-approved", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_anonymous_user_cannot_view_soft_deleted_cars(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_deleted(car)
        response = self.client.get(
            reverse("car-detail-soft-deleted", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_cannot_view_soft_deleted_cars(self):
        owner = self.create_customer("owner@gmail.com")
        car = self.create_car(owner=owner)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_deleted(car)

        self.client.force_authenticate(user=owner.user)

        response = self.client.get(
            reverse("car-detail-soft-deleted", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_can_view_soft_deleted_cars(self):
        customer = self.create_customer("test@gmail.com")
        employee = self.create_employee_worker("test1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_deleted(car)

        self.client.force_authenticate(user=employee.user)

        response = self.client.get(
            reverse("car-detail-soft-deleted", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_inactive_employee_cannot_view_soft_deleted_cars(self):
        customer = self.create_customer("test1@gmail.com")
        employee = self.create_employee_worker("inactive@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_deleted(car)
        employee = self.mark_employee_as_inactive(employee)

        self.client.force_authenticate(user=employee.user)

        response = self.client.get(
            reverse("car-detail-soft-deleted", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_view_soft_deleted_cars(self):
        customer = self.create_customer("customer@gmail.com")
        super_user = self.create_superuser("superuser@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        car = self.mark_car_as_deleted(car)

        self.client.force_authenticate(user=super_user)

        response = self.client.get(
            reverse("car-detail-soft-deleted", args=[car.id]),
            {},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_employee_can_soft_delete_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_admin("testuser2@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)

        self.client.force_authenticate(user=employee.user)
        response = self.client.put(
            reverse("car-soft-delete", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, True)

    def test_inactive_admin_employee_cannot_soft_delete_car(self):
        customer = self.create_customer("testuser1@gmail.com")
        employee = self.create_employee_admin("testuser2@gmail.com")
        employee = self.mark_employee_as_inactive(employee)
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        self.client.force_authenticate(user=employee.user)
        response = self.client.put(
            reverse("car-soft-delete", args=[car.id]),
            {},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        car.refresh_from_db()
        self.assertEqual(car.is_deleted, False)

    def test_superuser_cannot_update_car_that_belongs_to_owner(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        superuser = self.create_superuser("testuser2@gmail.com")
        self.client.force_authenticate(user=superuser)
        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            {
                "brand": "BMW",
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_update_car_that_belongs_to_owner(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        employee = self.create_employee_worker("testuser2@gmail.com")
        self.client.force_authenticate(user=employee.user)
        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            {
                "brand": "BMW",
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_can_update_critical_moderation_fields_of_own_car_and_updates_moderation_status_to_pending(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        self.client.force_authenticate(user=customer.user)
        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            {
                "brand": "BMW",
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.moderation_status, ModerationStatus.PENDING)
        self.assertEqual(car.reviewer, None)

    def test_customer_can_update_non_critical_moderation_fields_of_own_car_and_does_not_update_moderation_status(self):
        customer = self.create_customer("testuser1@gmail.com")
        car = self.create_car(owner=customer)
        car = self.mark_car_as_approved(car)
        self.client.force_authenticate(user=customer.user)
        response = self.client.patch(
            reverse("car-detail-update", args=[car.id]),
            {
                "description": "This is a new car",
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        car.refresh_from_db()
        self.assertEqual(car.description, "This is a new car")
        self.assertEqual(car.moderation_status, ModerationStatus.APPROVED)
        self.assertFalse(car.reviewer is None)