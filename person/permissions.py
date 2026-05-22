from rest_framework.permissions import BasePermission
from .models import Employee

class IsCustomer(BasePermission):
    """
    Ensures that a user is a customer
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'customer_profile')


class IsEmployeeActive(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
            
        return (
            hasattr(request.user, "employee_profile")
            and request.user.employee_profile.employment_status == Employee.EmploymentStatus.ACTIVE
        )


class IsEmployeeAdmin(BasePermission):
    """
    Custom permission allowing only employee admins
    (or Django superusers) to access certain views.
    """
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True

        if not hasattr(request.user, 'employee_profile'):
            return False
        
        if request.user.employee_profile.employment_status != Employee.EmploymentStatus.ACTIVE:
            return False

        return request.user.employee_profile.role == 'admin'
    

class IsAnonymous(BasePermission):
    """
    Prevent logged-in users from creating additional accounts
    """
    def has_permission(self, request, view):
        return not request.user.is_authenticated 