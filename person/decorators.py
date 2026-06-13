from functools import wraps
from django.http import HttpResponseForbidden
from .models import Employee

def active_employee_required(view_func):
    """
    Decorator to ensure the user is an active employee.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        
        try:
            employee_profile = request.user.employee_profile
        except Employee.DoesNotExist:
            return HttpResponseForbidden("You must be an employee to access this page.")
        
        if employee_profile.employment_status != Employee.EmploymentStatus.ACTIVE:
            return HttpResponseForbidden("Your employment status does not allow you to access this page.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_employee_required(view_func):
    """
    Decorator to ensure the user is an employee with admin role.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        
        try:
            employee_profile = request.user.employee_profile
        except Employee.DoesNotExist:
            return HttpResponseForbidden("You must be an employee to access this page.")
        
        if employee_profile.role != Employee.EmployeeRole.ADMIN:
            return HttpResponseForbidden("You do not have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def block_superuser_access(view_func):
    """
    Decorator to block superuser access to employee_profile required views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return HttpResponseForbidden("Only employees can access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view