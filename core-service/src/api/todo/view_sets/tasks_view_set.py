from typing import Any, cast

from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.oauth.permissions import ObjectPermissions
from apps.todo.models import Projects, Tasks, TaskStatus
from apps.todo.pagination import StandardPageNumberPagination
from apps.todo.serializers.tasks_serializers import (
    TaskChangeSerializer,
    TaskCreateSerializer,
)
from apps.todo.services.task_service import TaskService
from services import RedisService
from services.kafka_producer_service import KafkaProducerService, ModelEventsType

@extend_schema_view(
    list=extend_schema(tags=["Tasks"]),
    retrieve=extend_schema(tags=["Tasks"]),
    destroy=extend_schema(tags=["Tasks"]),
    create=extend_schema(tags=["Tasks"]),
    update=extend_schema(tags=["Tasks"]),
    partial_update=extend_schema(tags=["Tasks"]),
)
class TasksViewSet(ModelViewSet):
    task_service = TaskService(redis_service=RedisService())
    kafka_producer_service = KafkaProducerService()

    pagination_class = StandardPageNumberPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ["title", "created_at"]
    filter_fields = ["title", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        project = self.get_project()
        request: Request = cast(Request, self.request)
        filter_query = Q()
        for field in self.filter_fields:
            filter_value = request.query_params.get(field)
            if filter_value is not None:
                filter_query &= Q(**{field: filter_value})

        return project.tasks_set.filter(filter_query)

    def get_serializer_class(self):
        match self.action:
            case "create":
                return TaskCreateSerializer
            case _:
                return TaskChangeSerializer

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(project=self.get_project())
        return context

    def get_permissions(self):
        default_perms = super().get_permissions()
        match self.action:
            case "create":
                default_perms.append(ObjectPermissions("todo.add_tasks"))
            case "update":
                default_perms.append(ObjectPermissions("todo.change_tasks"))
            case "partial_update":
                default_perms.append(ObjectPermissions("todo.change_tasks"))
            case "destroy":
                default_perms.append(ObjectPermissions("todo.delete_tasks"))
        return default_perms

    def perform_create(self, serializer: TaskCreateSerializer):
        task = serializer.save(
            creator_user=self.request.user,
            project=self.get_project(),
            status=TaskStatus.CREATED,
        )
        self.kafka_producer_service.send_model_event(
            event_type=ModelEventsType.TaskCreated,
            object_id=task.id,
            object_data=serializer.data,
        )

    def perform_update(self, serializer: TaskChangeSerializer):
        task: Tasks = serializer.instance
        old_status = task.status
        save_kwargs: dict[str, Any] = {}

        if (
            "deadline" in serializer.validated_data.keys()
            and task.deadline != serializer.validated_data["deadline"]
        ):
            save_kwargs.update({"notification_sent": False})
            if task.reminder_task_id:
                self.task_service.cancel_deadline_notification(task.reminder_task_id)
                save_kwargs.update({"reminder_task_id": None})

        serializer.save(**save_kwargs)
        if task.status != old_status:
            self.task_service.send_task_statuses_notification(
                task_id=task.id,
            )
        self.kafka_producer_service.send_model_event(
            event_type=ModelEventsType.TaskUpdated,
            object_id=str(task.id),
            object_data=serializer.data,
        )

    def perform_destroy(self, instance):
        self.kafka_producer_service.send_model_event(
            event_type=ModelEventsType.TaskDeleted,
            object_id=instance.id,
            object_data={},
        )
        super().perform_destroy(instance)

    @extend_schema(tags=["Subscriptions"])
    @action(
        detail=True,
        methods=["delete"],
        url_path="status/subscription",
    )
    def delete_status_subscription(self, request, **_):
        task = self.get_object()
        if not self.task_service.unsubscribe_on_task_statuses(
            request.user.id,
            task.id,
        ):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["Subscriptions"])
    @action(
        detail=True,
        methods=["post"],
        url_path="status/subscription",
    )
    def post_status_subscription(self, request, **_):
        task = self.get_object()
        if not self.task_service.subscribe_on_task_statuses(
            request.user.id,
            task.id,
        ):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_204_NO_CONTENT)
