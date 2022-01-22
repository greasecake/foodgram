from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user == obj.author


class IsOwnerOrAdminOrReadOnly(IsOwnerOrAdmin):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        else:
            return super().has_object_permission(request, view, obj)
