from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated

class IsAdminUser(permissions.BasePermission):
    """
    Allow access only to admin users (is_staff=True)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

class IsSuperUser(permissions.BasePermission):
    """
    Allow access only to superusers
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser

class CustomAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff