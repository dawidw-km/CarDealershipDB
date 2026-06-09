from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from cars.serializers import CarRegistrationSerializer, ModerationStatusUpdateSerializerApproved, ModerationStatusUpdateSerializerRejected
from cars.models import Car, Status, ModerationStatus
from person.decorators import active_employee_required
@login_required(login_url="login-form")
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

    cars = Car.objects.filter(owner=request.user.customer_profile)

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