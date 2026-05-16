from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from ..models import Employee
from ..serializers import (
    AdminEmployeeEmploymentStatusUpdateSerializer,
    CustomerRegistrationSerializer,
    CustomerDetailSerializer,
    PasswordChangeSerializer,
    AdminEmployeeUpdateSerializer,
)
from person.decorators import (
    active_employee_required,
    admin_employee_required
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
            
            if hasattr(user, 'customer_profile'):
                return redirect("customer-profile")
            
            if hasattr(user, 'employee_profile'):
                return redirect("employee-profile")
        
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
def password_change_view(request):
    """
    Render a form to change the authenticated user's password.
    """
    if request.method == 'POST':
        serializer = PasswordChangeSerializer(data=request.POST)
        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data['old_password']):
                return render(
                    request,
                    "person/password_change.html",
                    {'error': 'Wrong password.'}
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return redirect("customer-login-form")
        
        return render(
            request,
            "person/password_change.html",
            {"errors": serializer.errors}
        )
    return render(
        request,
        "person/password_change.html"
    )

@login_required(login_url="customer-login-form")
def customer_profile_view(request):
    """
    Render the authenticated customer's profile page.
    """

    if not hasattr(request.user, 'customer_profile'):
        return redirect("customer-login-form")

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

    if not hasattr(request.user, 'customer_profile'):
        return redirect("customer-login-form")

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

@login_required(login_url="customer-login-form")
@active_employee_required
def employee_profile_view(request):
    """
    Render a dashboard page for employees.
    """

    if not hasattr(request.user, 'employee_profile'):
        return redirect("customer-login-form")

    employee = request.user.employee_profile

    return render(
        request,
        "person/employee_profile.html",
        {"employee": employee}
    )

@login_required(login_url="customer-login-form")
@active_employee_required
@admin_employee_required
def employee_list_view(request):
    """
    Render a list of all employees for employee admins.
    """
    
    employees = Employee.objects.all()
    return render(
        request,
        "person/employee_list.html",
        {"employees": employees}
    )

@login_required(login_url="customer-login-form")
@active_employee_required
@admin_employee_required
def admin_employee_update_view(request, pk):
    """
    Render a form for employee admins to update employee profiles.
    """
    
    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return redirect("employee-list")

    if request.method == "POST":
        serializer = AdminEmployeeUpdateSerializer(
            employee,
            data=request.POST,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return redirect("employee-list")

        return render(
            request,
            "person/admin_employee_update.html",
            {
                "employee": employee,
                "errors": serializer.errors
            }
        )

    return render(
        request,
        "person/admin_employee_update.html",
        {"employee": employee}
    )


@login_required(login_url="customer-login-form")
@active_employee_required
@admin_employee_required
def admin_employee_employment_status_update_view(request, pk):
    """
    Render a form for employee admins to update employee employment status.
    """
    
    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return redirect("employee-list")
    
    if request.method == "POST":
        serializer = AdminEmployeeEmploymentStatusUpdateSerializer(
            employee,
            data=request.POST
        )

        if serializer.is_valid():
            serializer.save()
            return redirect("employee-list")
        
        return render(
            request,
            "person/admin_employee_employment_status_update.html",
            {
                "employee": employee,
                "errors": serializer.errors
            }
        )

    return render(
        request,
        "person/admin_employee_employment_status_update.html",
        {"employee": employee}
    )