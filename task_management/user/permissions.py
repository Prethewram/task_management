from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()

class IsAdminOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin()

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.assigned_to == request.user:
            return True
        if request.user.is_admin() and (
            obj.created_by == request.user or
            obj.assigned_to.managed_by == request.user or
            request.user.is_superadmin()
        ):
            return True
        return False