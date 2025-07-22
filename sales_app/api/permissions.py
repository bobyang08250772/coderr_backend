from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated


class IsReviewerSelf(IsAuthenticated):
    """
    Only the reviewer can modify the review.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(request.user, 'userprofile') and request.user.userprofile == obj.reviewer


class IsUserWithProfile(IsAuthenticated):
    """
    User must be authenticated and have a profile for unsafe methods.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return super().has_permission(request, view)
        return super().has_permission(request, view) and hasattr(request.user, 'userprofile') and request.user.userprofile.type == 'customer'


class IsStaffForDeleteOrBusinessForPatch(IsAuthenticated):
    """
    Allow DELETE for staff/superusers, PATCH for business users.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if request.method == 'DELETE':
            return user.is_staff or user.is_superuser
        elif request.method == 'PATCH':
            return hasattr(user, 'userprofile') and user.userprofile.type == 'business'
        return False


class IsCustomerUser(IsAuthenticated):
    """
    Allow access only to authenticated users with a profile.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view) and hasattr(request.user, 'userprofile') and request.user.userprofile.type == 'customer'


class IsBusinessUser(IsAuthenticated):
    """
    Allow access only to business users.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view) and hasattr(request.user, 'userprofile') and request.user.userprofile.type == 'business'


class IsBusinessOwerOrReadOnly(IsAuthenticated):
    """
    Only the business owner can modify; others can read.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return hasattr(request.user, 'userprofile') and request.user.userprofile == obj.user_profile
