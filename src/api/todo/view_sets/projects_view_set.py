from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.request import Request

from apps.oauth.permissions import (
    DjangoPermissions,
    IsVerifiedAndAuthenticated,
)
from apps.todo.models import Projects, ProjectUsers
from apps.todo.pagination import StandardPageNumberPagination
from apps.todo.serializers import ProjectSerializer


class ProjectsViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        project_users = ProjectUsers.objects.filter(user=self.request.user)
        queryset = Projects.objects.filter(projectusers__in=project_users)
        if self.action != "retrieve":
            queryset = queryset.annotate(users_count=Count("projectusers"))
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            detailed=(self.action == "retrieve"),
        )
        return context

    def get_permissions(self):
        permissions = [permission() for permission in self.permission_classes]
        if self.action in ("update", "destroy", "create"):
            permissions.append(DjangoModelPermissions())
        return permissions

    def perform_create(self, serializer):
        project = serializer.save(creator_user=self.request.user)
        proj_user = ProjectUsers(project=project, user=self.request.user)
        proj_user.save()
        project.users_count = ProjectUsers.objects.filter(project=project).count()

    def perform_update(self, serializer):
        serializer.save(creator_user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsVerifiedAndAuthenticated,
            DjangoPermissions("todo.add_projectusers"),
        ],
        url_path="invitation-link",
    )
    def invitation_link(self, request: Request, pk=None):
        # TODO: User создает пригласительную-ссылку
        #  (данные хранятся в виде JSON в Redis):
        #  - указывает доступы
        #  - указывает почты пользователей
        #  (если не указывает, то ссылка действует для любого юзера)
        #  - время действия ссылки (по дефолту 1 сутки)
        raise NotImplementedError("Not implemented")

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsVerifiedAndAuthenticated],
        url_path="invitation-accept",
    )
    def invitation_accept(self, request: Request):
        # TODO: Отправка приглашения на проект:
        #    Пользователь получает ссылку:
        #     - если отсутствует аккаунт, то регистрируется
        #     с соответствующей верифицированной почтой
        #     - получает доступ к проекту
        raise NotImplementedError("Not implemented")
