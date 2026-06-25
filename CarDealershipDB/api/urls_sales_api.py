from django.urls import path
from sales.views.api_views import (
    SaleRegistrationView,
    BuyerSalesListView,
    OwnerSalesListView,
    StaffSalesListView,
)

urlpatterns = [
    path(
        "sales/cars/<int:pk>/register/",
        SaleRegistrationView.as_view(),
        name="sale-car-registration"
        ),
    path(
        "sales/buyer/list/",
        BuyerSalesListView.as_view(),
        name="buyer-sales-list"
        ),
    path(
        "sales/owner/list/",
        OwnerSalesListView.as_view(),
        name="owner-sales-list"
        ),
    path(
        "sales/staff/list/",
        StaffSalesListView.as_view(),
        name="staff-sales-list"
        ),
]