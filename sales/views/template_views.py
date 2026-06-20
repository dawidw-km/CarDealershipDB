from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from cars.models import Car, Status, ModerationStatus
from sales.serializers import SaleRegistrationSerializer

@login_required(login_url="login-form")
def customer_sale_registration_view(request, pk):
    """
    Render a form for customers to register a sale for a car.
    """
    if not hasattr(request.user, 'customer_profile'):
        raise PermissionDenied

    car = get_object_or_404(Car, id=pk)

    if car.status == Status.RESERVED and car.buyer != request.user.customer_profile:
        raise PermissionDenied

    if car.status == Status.SOLD:
        raise PermissionDenied

    if car.moderation_status != ModerationStatus.APPROVED:
        raise PermissionDenied

    if car.owner == request.user.customer_profile:
        raise PermissionDenied
    
    if request.method == "POST":
        serializer = SaleRegistrationSerializer(data=request.POST, context={"request": request, "car": car})
        if serializer.is_valid():
            serializer.save()
            return redirect("customer-profile")

        return render(
            request,
            "sales/customer_sale_registration_form.html",
            {"errors": serializer.errors, "car": car, "request": request}
        )

    return render(
        request,
        "sales/customer_sale_registration_form.html",
        {"car": car}
    )