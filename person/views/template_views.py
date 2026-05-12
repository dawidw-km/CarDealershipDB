from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from ..serializers import (
    CustomerRegistrationSerializer,
    CustomerDetailSerializer,
)

def login_view(request):
    """
    Render login form and authenticate users.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("customer-profile")
        
        return render(
            request,
            "person/login.html",
            {"error": "Invalid email or password."}
        )
    
    return render(
        request,
        "person/login.html"
    )


def customer_registration_view(request):
    """
    Render customer registration form and create customer accounts.
    """
    if request.method == "POST":
        serializer = CustomerRegistrationSerializer(data=request.POST)

        if serializer.is_valid():
            serializer.save()
            return redirect("customer-login-form")
        
        return render(
            request,
            "person/customer_registration.html",
            {"errors": serializer.errors}
        )
    
    return render(
        request,
        "person/customer_registration.html"
    )


@login_required(login_url="customer-login-form")
def customer_profile_view(request):
    """
    Render the authenticated customer's profile page.
    """

    customer = request.user.customer_profile

    return render(
        request,
        "person/customer_profile.html",
        {"customer": customer}
    )


@login_required(login_url="customer-login-form")
def customer_profile_update_view(request):
    """
    Render a form to update the authenticated customer's profile.
    """
    customer = request.user.customer_profile

    if request.method == "POST":
        serializer = CustomerDetailSerializer(
            customer,
            data=request.POST,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return redirect("customer-profile")

        return render(
            request,
            "person/customer_profile_update.html",
            {
                "customer": customer,
                "errors": serializer.errors
            }
        )

    return render(
        request,
        "person/customer_profile_update.html",
        {"customer": customer}
    )