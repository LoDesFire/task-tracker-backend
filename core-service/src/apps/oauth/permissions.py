from rest_framework import permissions

from helpers.exceptions import UnknownObject


class IsVerifiedAndAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_verified
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.is_superuser
        )


class ModelPermissions(permissions.BasePermission):
    def __init__(self, *required_permissions):
        self.required_permissions = set(required_permissions)

    def __call__(self, *args, **kwargs):
        return self

    def has_permission(self, request, view):
        return request.user.has_perms(self.required_permissions)


class ObjectPermissions(ModelPermissions):
    def __call__(self, *args, **kwargs):
        return self

    def has_object_permission(self, request, view, obj):
        try:
            return request.user.has_perms(
                self.required_permissions,
                obj=obj,
            )
        except UnknownObject:
            # skip permissions checking
            return True
