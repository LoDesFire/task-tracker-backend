from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.oauth.models import Users
from apps.todo.models import Projects, ProjectUsers
from services.permissions_service import PermissionsService
from services.serializers.project_permissions_serializers import (
    ProjectPermissionsChangeSerializer,
)


class ProjectUserPermissionsViewSet(GenericViewSet):
    def get_queryset(self):
        project = self.get_project()
        return Users.objects.filter(projectusers__project=project)

    def get_project(self) -> Projects:
        project_pk = self.kwargs.get("projects_pk")
        if self.request.user.is_superuser:
            objects_queryset = Projects.objects.filter()
        else:
            objects_queryset = Projects.objects.filter(
                projectusers__user=self.request.user,
            )
        project = get_object_or_404(
            queryset=objects_queryset,
            pk=project_pk,
        )

        self.check_object_permissions(self.request, project)

        return project

    @extend_schema(tags=["Project Permissions"])
    def retrieve(self, request: Request, **_):
        project = self.get_project()
        user: Users = self.get_object()

        if not (
            (
                request.user.has_perm("todo.add_projectuserpermissions", obj=project)
                or request.user.has_perm(
                    "todo.change_projectuserpermissions", obj=project
                )
                or request.user.has_perm(
                    "todo.delete_projectuserpermissions", obj=project
                )
            )
            and user.id != request.user.id
        ):
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        response = {
            "user_id": user.id,
            "permissions": {
                "allowed": PermissionsService.get_available_permissions(user, project),
                "restricted": PermissionsService.get_restricted_permissions(
                    user,
                    project,
                ),
            },
            "group_permissions": PermissionsService.get_available_group_permissions(
                user,
                project,
            ),
        }

        return Response(response, status=status.HTTP_200_OK)

    @extend_schema(tags=["Project Permissions"])
    def update(self, request: Request, **_):
        project = self.get_project()
        user: Users = self.get_object()

        if request.user == user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        if not (
            request.user.has_perm("todo.add_projectuserpermissions", obj=project)
            or request.user.has_perm("todo.change_projectuserpermissions", obj=project)
            or request.user.has_perm("todo.delete_projectuserpermissions", obj=project)
        ):
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        request_serializer = ProjectPermissionsChangeSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        allowed_permissions = request_serializer.validated_data["permissions"][
            "allowed"
        ]
        restricted_permissions = request_serializer.validated_data["permissions"][
            "restricted"
        ]
        groups = request_serializer.validated_data["groups"]

        if not PermissionsService.is_project_permissions_available_for_user(
            project, request.user, allowed_permissions
        ) or not PermissionsService.is_project_groups_available_for_user(
            project, request.user, groups
        ):
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            project_user = ProjectUsers.objects.filter(
                project=project, user=user
            ).first()
            project_user.permissions.set([])
            project_user.permissions.add(
                *restricted_permissions,
                through_defaults={"restrict": True},
            )
            project_user.permissions.add(
                *allowed_permissions,
                through_defaults={"restrict": False},
            )
            project_user.groups.set(groups)

        response = {
            "user_id": user.id,
            "permissions": {
                "allowed": PermissionsService.get_available_permissions(user, project),
                "restricted": PermissionsService.get_restricted_permissions(
                    user,
                    project,
                ),
            },
            "group_permissions": PermissionsService.get_available_group_permissions(
                user,
                project,
            ),
        }

        return Response(response, status=200)
