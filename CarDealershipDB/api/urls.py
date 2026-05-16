from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView
from cars.views import CarViewSet
from person.views.api_views import (
    CustomerDetailView,
    CustomerRegistrationView,
    EmployeeRegistrationView,
    EmployeeListView,
    CustomerDetailView,
    ChangePasswordView,
    AdminEmployeeUpdateView,
    AdminEmployeeEmploymentStatusUpdateView,
    EmployeeLoginView,
)

router = routers.DefaultRouter()
router.register(
    r"cars",
    CarViewSet
    )

urlpatterns = [
    # API urls
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
    path(
        "employee/token/",
        EmployeeLoginView.as_view(),
        name="employee-token-obtain-pair"
        ),
    path(
        "employee/token/refresh/",
        TokenRefreshView.as_view(),
        name="employee-token-refresh"
        ),
]