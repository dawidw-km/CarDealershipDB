from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from cars.serializers import CarRegistrationSerializer

@login_required(login_url="customer-login-form")
def customer_car_registration_view(request):
    """
    Render a form for customers to register a new car.
    """
    if not hasattr(request.user, 'customer_profile'):
        raise PermissionDenied("You must be a customer to register a car.")

    if request.method == "POST":
        serializer = CarRegistrationSerializer(data=request.POST)

        if serializer.is_valid():
            serializer.save(owner=request.user.customer_profile)
            return redirect("customer-profile")

        return render(
            request,
            "cars/customer_car_registration.html",
            {"errors": serializer.errors}
        )

    return render(
        request,
        "cars/customer_car_registration.html",
    )