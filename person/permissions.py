from rest_framework.permissions import BasePermission


class IsEmployee(BasePermission):
    """
    Ensures that a user is an employee
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'employee_profile')


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

        return request.user.employee_profile.role == 'admin'
    

class IsAnonymous(BasePermission):
    """
    Prevent logged-in users from creating additional accounts
    """
    def has_permission(self, request, view):
        return not request.user.is_authenticated 