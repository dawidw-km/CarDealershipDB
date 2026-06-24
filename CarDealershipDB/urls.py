from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("CarDealershipDB.api.urls")),
    path("docs/", include("CarDealershipDB.docs.urls")),
    path("", include("CarDealershipDB.templates.urls_cars_template")),
    path("", include("CarDealershipDB.templates.urls_person_templates")),
    path("", include("CarDealershipDB.templates.urls_sales_template")),
]