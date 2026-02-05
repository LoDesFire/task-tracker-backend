import logging

from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from django.db.models import Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import decorators, status, viewsets
from rest_framework.permissions import SAFE_METHODS, DjangoModelPermissions
from rest_framework.request import Request
from rest_framework.response import Response

from apps.oauth.models import GroupName
from apps.oauth.permissions import ObjectPermissions
from apps.todo.models import Projects, ProjectUserPermissions, ProjectUsers
from apps.todo.pagination import StandardPageNumberPagination
from apps.todo.serializers import InviteOutputSerializer, ProjectSerializer
from services import InvitationService
from services.kafka_producer_service import KafkaProducerService, ModelEventsType

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(tags=["Projects"]),
    retrieve=extend_schema(tags=["Projects"]),
    destroy=extend_schema(tags=["Projects"]),
    create=extend_schema(tags=["Projects"]),
    update=extend_schema(tags=["Projects"]),
    partial_update=extend_schema(tags=["Projects"]),
)
class ProjectsViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    pagination_class = StandardPageNumberPagination
    kafka_producer_service = KafkaProducerService()

    def get_queryset(self):
        if self.request.user.is_superuser:
            user_project_ids = Projects.objects.all().values_list("id", flat=True)
        else:
            user_project_ids = Projects.objects.filter(
                projectusers__user=self.request.user,
            ).values_list("id", flat=True)
        queryset = Projects.objects.filter(id__in=user_project_ids)
        if self.action != "retrieve":
            queryset = queryset.annotate(users_count=Count("projectusers"))
        return queryset.order_by("id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(detailed=(self.action == "retrieve"))
        return context

    def get_permissions(self):
        permissions = [permission() for permission in self.permission_classes]
        match self.action:
            case "update":
                permissions.append(ObjectPermissions("todo.change_projects"))
            case "destroy":
                permissions.append(ObjectPermissions("todo.delete_projects"))
        if self.action not in SAFE_METHODS:
            permissions.append(DjangoModelPermissions())

        return permissions

    def perform_create(self, serializer):
        project = serializer.save(creator_user=self.request.user)
        proj_user = ProjectUsers(
            project=project,
            user=self.request.user,
            is_active=True,
            is_owner=True,
        )
        proj_user.save()
        project_users_group = Group.objects.get(name=GroupName.PROJECT_ALL)
        proj_user.groups.add(project_users_group, through_defaults={})
        project.users_count = ProjectUsers.objects.filter(project=project).count()

        self.kafka_producer_service.send_model_event(
            event_type=ModelEventsType.ProjectCreated,
            object_id=project.id,
            object_data=serializer.data,
        )
        self.kafka_producer_service.send_model_event(
            event_type=ModelEventsType.UserEnteredProject,
            object_id=str(proj_user.id),
            object_data=proj_user.__dict__,
        )

    def perform_destroy(self, instance):
        self.kafka_producer_service.send_model_event(
            event_type=ModelEventsType.ProjectDeleted,
            object_id=instance.id,
            object_data={},
        )

        super().perform_destroy(instance)

    @extend_schema(tags=["Invitations"])
    @decorators.action(
        detail=True,
        methods=["post"],
        permission_classes=[ObjectPermissions("todo.add_projectusers")],
        url_path="invitation-link",
    )
    def invitation_link(self, request: Request, pk=None):
        project = self.get_object()
        invitation = InvitationService.create_invitation(
            request.user,
            project,
            invitation_data=request.data,
        )
        invitation_serializer = InviteOutputSerializer(data=invitation)

        if not invitation_serializer.is_valid():
            logger.warning(
                "Failed to serialize invitation output. %s",
                str(invitation_serializer.errors),
            )
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if invitation["emails"] is not None and len(invitation["emails"]) > 0:
            InvitationService.send_invitation_emails(
                *invitation["emails"],
                invitation_id=str(
                    invitation_serializer.validated_data["invitation_id"]
                ),
            )

        return Response(invitation_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=["Invitations"])
    @decorators.action(
        detail=False,
        methods=["post"],
        url_path="invitation-accept",
    )
    def invitation_accept(self, request: Request):
        invitation_info = InvitationService.get_invitation(request.data)

        if invitation_info is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                project_users = ProjectUsers.objects.create(
                    project=invitation_info["project"],
                    user=self.request.user,
                    is_active=True,
                )

                project_users.groups.set(invitation_info["permission_groups"])
                project_users.permissions.set(invitation_info["permissions"])

                restricted_permissions = invitation_info["restricted_permissions"]
                ProjectUserPermissions.objects.bulk_create(
                    objs=[
                        ProjectUserPermissions(
                            project_user=project_users,
                            restrict=True,
                            permission=permission,
                        )
                        for permission in restricted_permissions
                    ],
                )

        except IntegrityError as exc:
            logger.warning("Invitation create error: %s", str(exc))
            return Response(status=status.HTTP_409_CONFLICT)

        self.kafka_producer_service.send_model_event(
            event_type=ModelEventsType.UserEnteredProject,
            object_id=str(project_users.id),
            object_data=project_users.__dict__,
        )

        return Response(status=status.HTTP_200_OK)
