from django.urls import path, include
from person.views.api_views import (
    EmployeeLoginView,
    CustomerLoginView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
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
]