from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsReviewerSelf(permissions.BasePermission):
    """
    Custom permission: Allow business users to post.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(request.user, 'userprofile'):
            return request.user and request.user.is_authenticated and request.user.userprofile == obj.reviewer
        else:
            return False

class IsUserWithProfile(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and hasattr(request.user, 'userprofile')
    

class IsStaffForDeleteOrBusinessForPatch(permissions.BasePermission):
    """
    Custom permission: Allow staff users to patch and delete.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS:
            return True
        elif request.method == 'DELETE':
            return user and user.is_authenticated and (user.is_staff or user.is_superuser)
        elif request.method == 'PATCH':
            if hasattr(request.user, 'userprofile'):
                return user and user.is_authenticated and user.userprofile.type == 'business'
            else:
                return False
        return False


class IsCustomerUser(permissions.BasePermission):
    """
    Custom permission: Allow customer users to post.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if hasattr(request.user, 'userprofile'):
            return request.user and request.user.is_authenticated and request.user.userprofile.type == 'customer'
        else:
            return False
        

class IsBusinessUser(permissions.BasePermission):
    """
    Custom permission: Allow business users to post.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if hasattr(request.user, 'userprofile'):
            return request.user and request.user.is_authenticated and request.user.userprofile.type == 'business'
        else:
            return False
        


class IsBusinessOwerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Allow business users to update.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        if hasattr(request.user, 'userprofile'):
            return request.user and request.user.is_authenticated and request.user.userprofile == obj.user_profile
        else:
            return False
        