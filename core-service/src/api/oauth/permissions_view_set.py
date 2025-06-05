from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.oauth.models import Users
from apps.oauth.permissions import IsAdmin
from services.permissions_service import PermissionsService
from services.serializers.project_permissions_serializers import (
    ProjectPermissionsChangeSerializer,
)


class UserPermissionsViewSet(GenericViewSet):
    queryset = Users.objects.all()
    permission_classes = (IsAdmin,)

    @extend_schema(tags=["User Permissions"])
    def retrieve(self, request: Request, **_):
        user: Users = self.get_object()

        response = {
            "user_id": user.id,
            "permissions": {
                "allowed": PermissionsService.get_available_permissions(user),
                "restricted": PermissionsService.get_restricted_permissions(user),
            },
            "group_permissions": PermissionsService.get_available_group_permissions(
                user,
            ),
        }

        return Response(response, status=status.HTTP_200_OK)

    @extend_schema(tags=["User Permissions"])
    def update(self, request: Request, **_):
        user: Users = self.get_object()

        request_serializer = ProjectPermissionsChangeSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        allowed_permissions = request_serializer.validated_data["permissions"][
            "allowed"
        ]
        restricted_permissions = request_serializer.validated_data["permissions"][
            "restricted"
        ]
        groups = request_serializer.validated_data["groups"]

        with transaction.atomic():
            user = Users.objects.filter(id=user.id).first()
            user.user_permissions.set([])
            user.user_permissions.add(
                *restricted_permissions,
                through_defaults={"restrict": True},
            )
            user.user_permissions.add(
                *allowed_permissions,
                through_defaults={"restrict": False},
            )
            user.groups.set(groups)

        response = {
            "permissions": {
                "allowed": PermissionsService.get_available_permissions(user),
                "restricted": PermissionsService.get_restricted_permissions(user),
            },
            "group_permissions": PermissionsService.get_available_group_permissions(
                user,
            ),
        }

        return Response(response, status=200)
