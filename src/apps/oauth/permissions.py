from rest_framework import permissions


class IsVerifiedAndAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_verified
        )


class DjangoPermissions(permissions.DjangoModelPermissions):
    def __init__(self, *required_permissions):
        self.required_permissions = set(required_permissions)

    def __call__(self, *args, **kwargs):
        return self

    def has_permission(self, request, view):
        return request.user.has_perms(self.required_permissions)
