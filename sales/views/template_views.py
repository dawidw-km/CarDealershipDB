from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from cars.models import Car, Status, ModerationStatus
from sales.models import Sale
from sales.serializers import SaleRegistrationSerializer
from person.decorators import active_employee_required


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


@login_required(login_url="login-form")
def buyer_sale_list_view(request):
    """
    Render a list of sales for the buyer.
    """
    if not hasattr(request.user, 'customer_profile'):
        raise PermissionDenied

    sales = Sale.objects.filter(
        buyer=request.user.customer_profile
    )
    if not sales.exists():
        return redirect("customer-profile")

    return render(
        request,
        "sales/sale_list.html",
        {"sales": sales}
    )


@login_required(login_url="login-form")
def owner_sale_list_view(request):
    """
    Render a list of sales for the owner.
    """
    if not hasattr(request.user, 'customer_profile'):
        raise PermissionDenied

    sales = Sale.objects.filter(
        seller=request.user.customer_profile
    )
    if not sales.exists():
        return redirect("customer-profile")

    return render(
        request,
        "sales/sale_list.html",
        {"sales": sales}
    )


@login_required(login_url="login-form")
@active_employee_required
def staff_sale_list_view(request):
    """
    Render a list of sales for the staff.
    """
    sales = Sale.objects.all()

    return render(
        request,
        "sales/sale_list.html",
        {"sales": sales}
    )