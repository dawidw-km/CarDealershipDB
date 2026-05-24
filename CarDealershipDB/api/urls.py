from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from cars.views.api_views import (
    CarRegistrationView,
    CarDetailUpdateView,
    CarModerationStatusUpdateView,
    CarDetailView,
    CarSoftDeleteView,
    )
from person.views.api_views import (
    CustomerDetailView,
    CustomerRegistrationView,
    EmployeeRegistrationView,
    EmployeeListView,
    EmployeeDetailView,
    ChangePasswordView,
    AdminEmployeeUpdateView,
    AdminEmployeeEmploymentStatusUpdateView,
    EmployeeLoginView,
    CustomerLoginView,
)

router = routers.DefaultRouter()

urlpatterns = [
    # API urls
    # Authentication urls
    path(
        "",
        include(router.urls)
        ),
    path(
        "api-auth/",
        include("rest_framework.urls",
        namespace="rest_framework")
        ),
    path(
        "employee/token/",
        EmployeeLoginView.as_view(),
        name="employee-token-obtain-pair"
        ),
    path(
        "customer/token/",
        CustomerLoginView.as_view(),
        name="customer-token-obtain-pair"
        ),
    path(
        "employee/token/refresh/",
        TokenRefreshView.as_view(),
        name="employee-token-refresh"
        ),
    # Customers urls
    path(
        "register/customer/",
        CustomerRegistrationView.as_view(),
        name="customer-registration"
        ),
    path(
        "customer/me/",
        CustomerDetailView.as_view(),
        name="customer-detail"
        ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change-password"
        ),
    # Employees urls
    path(
        "employee/me/",
        EmployeeDetailView.as_view(),
        name="employee-detail"
        ),
    path(
        "register/employee/",
        EmployeeRegistrationView.as_view(),
        name="employee-registration"
        ),
    path(
        "admin/employees/",
        EmployeeListView.as_view(),
        name="employee-list"
        ),
    path(
        "admin/employees/<int:pk>/",
        AdminEmployeeUpdateView.as_view(),
        name="admin-employee-update"
        ),
    path(
        "admin/employees/<int:pk>/employment-status/",
        AdminEmployeeEmploymentStatusUpdateView.as_view(),
        name="admin-employee-employment-status-update"
        ),
    # Cars urls
    path(
        "register/car/",
        CarRegistrationView.as_view(),
        name="car-registration"
        ),
    path(
        "cars/<int:pk>/update/",
        CarDetailUpdateView.as_view(),
        name="car-detail-update"
        ),
    path(
        "cars/<int:pk>/moderation-status/",
        CarModerationStatusUpdateView.as_view(),
        name="car-moderation-status-update"
        ),
    path(
        "cars/<int:pk>/",
        CarDetailView.as_view(),
        name="car-detail"
        ),
    path(
        "cars/soft-delete/<int:pk>/",
        CarSoftDeleteView.as_view(),
        name="car-soft-delete"
        ),
]