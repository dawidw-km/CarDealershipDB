from django.urls import path
from person.views.api_views import (
    CustomerRegistrationView,
    CustomerDetailView,
    CustomerListView,
    ChangePasswordView,
    EmployeeRegistrationView,
    EmployeeDetailView,
    EmployeeListView,
    AdminEmployeeUpdateView,
    AdminEmployeeEmploymentStatusUpdateView,
)

urlpatterns = [
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
        "customers/",
        CustomerListView.as_view(),
        name="customer-list"
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
]