from django.urls import path
from person.views.template_views import (
    customer_registration_view,
    login_view,
    customer_profile_view,
    customer_profile_update_view,
    customer_password_change_view,
)

urlpatterns = [
    path(
        "register/customer/form/",
        customer_registration_view,
        name="customer-registration-form"
    ),
    path(
        "login/customer/form/",
        login_view,
        name="customer-login-form"
    ),
    path(
        "customer/profile/",
        customer_profile_view,
        name="customer-profile"
    ),
    path(
        "customer/profile/update/",
        customer_profile_update_view,
        name="customer-profile-update"
    ),
    path(
        "customer/change-password/",
        customer_password_change_view,
        name="customer-change-password"
    )
]