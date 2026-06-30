from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from person.models import Employee
from cars.serializers import (
    CarRegistrationSerializer,
    ModerationStatusUpdateSerializerApproved,
    ModerationStatusUpdateSerializerRejected,
    CarDetailUpdateSerializer,
    CarSoftDeleteSerializer
)
from cars.models import (
    Car,
    Status,
    ModerationStatus,
    VehicleType,
    FuelType,
    Transmission,
    VehicleCondition,
    AccidentStatus
)
from person.decorators import (
    active_employee_required,
    block_superuser_access
)

@login_required(login_url="login-form")
def customer_car_registration_view(request):
    """
    Render a form for customers to register a new car.
    """
    if not hasattr(request.user, 'customer_profile'):
        raise PermissionDenied

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


def public_car_list_view(request):
    """
    Render a list of all cars available for purchase.
    """
    cars = Car.objects.filter(
        status=Status.AVAILABLE,
        is_deleted=False,
        moderation_status=ModerationStatus.APPROVED
        )
    return render(
        request,
        "cars/public_cars_list.html",
        {"cars": cars}
    )

@login_required(login_url="login-form")
def owner_car_list_view(request):
    """
    Render a list of all cars owned by the authenticated user.
    """
    if not hasattr(request.user, 'customer_profile'):
        raise PermissionDenied

    cars = Car.objects.filter(owner=request.user.customer_profile, is_deleted=False)

    if not cars.exists():
        return redirect("customer-profile")

    return render(
        request,
        "cars/owner_cars_list.html",
        {"cars": cars}
    )

@login_required(login_url="login-form")
@active_employee_required
def employee_deleted_cars_list_view(request):
    """
    Render a list of all deleted cars.
    """

    cars = Car.objects.filter(is_deleted=True)

    if not cars.exists():
        return redirect("employee-profile")

    return render(
        request,
        "cars/employee_deleted_cars_list.html",
        {"cars": cars}
    )

@login_required(login_url="login-form")
@active_employee_required
def employee_car_moderation_list_view(request):
    """
    Render a list of all cars pending moderation.
    """
    cars = Car.objects.filter(moderation_status=ModerationStatus.PENDING)
    return render(
        request,
        "cars/employee_car_moderation_list.html",
        {"cars": cars}
    )

@login_required(login_url="login-form")
@active_employee_required
@block_superuser_access
def employee_car_moderation_update_approved_view(request, pk):
    """
    Update the moderation status of a car.
    """
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return redirect("employee-car-moderation-list-template")

    if request.method == "POST":
        serializer = ModerationStatusUpdateSerializerApproved(
            car,
            data=request.POST,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return redirect("employee-car-moderation-list-template")
        
        return render(
            request,
            "cars/employee_car_moderation_list.html",
            {
                "car": car,
                "errors": serializer.errors
            }
        )

    return render(
        request,
        "cars/employee_car_moderation_list.html",
        {"car": car}
    )

@login_required(login_url="login-form")
@active_employee_required
@block_superuser_access
def employee_car_moderation_update_rejected_view(request, pk):
    """
    Update the moderation status of a car.
    """
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return redirect("employee-car-moderation-list-template")
        
    if request.method == "POST":
        serializer = ModerationStatusUpdateSerializerRejected(
            car,
            data=request.POST,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return redirect("employee-car-moderation-list-template")
    
        return render(
            request,
            "cars/employee_car_moderation_list.html",
            {
                "car": car,
                "errors": serializer.errors
            }
        )
    return render(
        request,
        "cars/employee_car_moderation_list.html",
        {"car": car}
    )

@login_required(login_url="login-form")
def owner_and_staff_car_soft_delete_view(request, pk):
    """
    Soft delete a car.
    """

    if hasattr(request.user, 'employee_profile'):
        if request.user.employee_profile.role == Employee.EmployeeRole.WORKER:
            raise PermissionDenied("Workers are not allowed to soft delete cars.")
        if request.user.employee_profile.employment_status != Employee.EmploymentStatus.ACTIVE:
            raise PermissionDenied("Inactive employees are not allowed to soft delete cars.")

    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        if hasattr(request.user, 'customer_profile'):
            return redirect("owner-cars-list-template")
        else:
            return redirect("public-car-list-template")

    if car.status == Status.RESERVED or car.status == Status.SOLD:
            raise PermissionDenied("You cannot soft delete a car that is reserved or sold.")
        
    if not request.user.is_superuser and not hasattr(request.user, 'employee_profile'):
        if car.owner != request.user.customer_profile:
            raise PermissionDenied("You cannot soft delete a car that you do not own.")

    if request.method == "POST":
        serializer = CarSoftDeleteSerializer(
            car,
            data=request.POST,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            if hasattr(request.user, 'customer_profile'):
                return redirect("owner-cars-list-template")
            elif request.user.is_superuser:
                return redirect("public-car-list-template")
            elif hasattr(request.user, 'employee_profile'):
                return redirect("public-car-list-template")
            
    if hasattr(request.user, 'customer_profile'):
        return render(
            request,
            "cars/owner_cars_list.html",
            {"car": car}
        )
    elif request.user.is_superuser:
        return render(
            request,
            "cars/public_cars_list.html",
            {"car": car}
        )
    elif hasattr(request.user, 'employee_profile'):
        return render(
            request,
            "cars/public_cars_list.html",
            {"car": car}
        )
    else:
        return redirect("login-form")


@login_required(login_url="login-form")
def owner_car_update_view(request, pk):
    """
    Render a form to update the details of a owner's car.
    """
    car_text_choices = {
        "vehicle_types": VehicleType.choices,
        "fuel_types": FuelType.choices,
        "transmissions": Transmission.choices,
        "vehicle_conditions": VehicleCondition.choices,
        "accident_statuses": AccidentStatus.choices,
    }

    if not hasattr(request.user, 'customer_profile'):
        raise PermissionDenied("You must be a customer to update a car.")

    try:
        car = Car.objects.get(
            pk=pk,
            owner=request.user.customer_profile,
            is_deleted=False,
            status=Status.AVAILABLE
            )
    except Car.DoesNotExist:
        return redirect("owner-cars-list-template")

    if request.method == "POST":
        serializer = CarDetailUpdateSerializer(
            car,
            data=request.POST,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return redirect("owner-cars-list-template")
        
        return render(
            request,
            "cars/owner_car_update.html",
            {
                "car": car,
                "errors": serializer.errors,
                "car_text_choices": car_text_choices,
            }
        )
    return render(
        request,
        "cars/owner_car_update.html",
        {
            "car": car,
            "car_text_choices": car_text_choices,
        }
    )