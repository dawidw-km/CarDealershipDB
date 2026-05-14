from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from cars.views import CarViewSet
from person.views.api_views import (
    CustomerDetailView,
    CustomerViewSet,
    EmployeeViewSet,
    CustomerRegistrationView,
    EmployeeRegistrationView,
    EmployeeListView,
    CustomerDetailView,
)

router = routers.DefaultRouter()
router.register(
    r"cars",
    CarViewSet
    )
router.register(
    r"customers",
    CustomerViewSet
    )
router.register(
    r"employees",
    EmployeeViewSet
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
        "api/customer/me/",
        CustomerDetailView.as_view(),
        name="customer-detail"
    ),
    path(
        "register/employee/",
        EmployeeRegistrationView.as_view(),
        name="employee-registration"
        ),
    path(
        "api/admin/employees/",
        EmployeeListView.as_view(),
        name="employee-list"
        ),
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
        ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
        ),
]