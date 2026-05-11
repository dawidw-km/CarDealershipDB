"""
URL configuration for CarDealershipDB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from cars.views import CarViewSet
from person.views import CustomerViewSet, EmployeeViewSet, CustomerRegistrationView, EmployeeRegistrationView
from person.views import EmployeeListView, CustomerDetailView, login_view, customer_registration_view

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
        'admin/',
        admin.site.urls
        ),
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
        
    # Template urls
    path(
        "register/customer/form/",
        customer_registration_view,
        name="customer-registration-form"
        ),
    path(
        "login/customer/form/",
        login_view,
        name="customer-login-form"
    )
]
