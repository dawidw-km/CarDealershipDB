from rest_framework.permissions import BasePermission
from cars.models import Status


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
    

class IsCarOwner(BasePermission):
    """
    Custom permission allowing user/staff to access only their own cars.
    """
    def has_object_permission(self, request, view, obj):

        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'employee_profile'):
            return True

        return(
            hasattr(request.user, 'customer_profile') and 
            obj.owner == request.user.customer_profile
        )
    

class CannotDeleteSoldCar(BasePermission):
    """
    Custom permission preventing deletion of sold cars.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return obj.status != Status.SOLD
        return True
    
    
class CannotModifySoldCar(BasePermission):
    """
    Custom permission preventing modification of sold cars.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return obj.status != Status.SOLD
        return True


class CanChangeCarModerationStatus(BasePermission):
    """
    Allow employees and superusers to moderate cars.
    """

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if not hasattr(request.user, 'employee_profile'):
            return False
        
        return True