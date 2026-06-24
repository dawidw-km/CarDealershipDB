from django.urls import path
from sales.views.template_views import (
    buyer_sale_list_view,
    owner_sale_list_view,
    staff_sale_list_view,
    customer_sale_registration_view
)

urlpatterns = [
    path(
        "customer/sale/register/<int:pk>/",
        customer_sale_registration_view,
        name="sale-car-registration-template"
    ),
    path(
        "buyer/sales/",
        buyer_sale_list_view,
        name="buyer-sales-list-template"
    ),
    path(
        "owner/sales/",
        owner_sale_list_view,
        name="owner-sales-list-template"
    ),
    path(
        "staff/sales/",
        staff_sale_list_view,
        name="staff-sales-list-template"
    ),
]