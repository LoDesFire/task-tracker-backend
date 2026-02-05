from enum import StrEnum

from django.contrib.auth.models import Group, Permission
from django.contrib.postgres.indexes import BTreeIndex
from django.db import models

from apps.oauth.models import Users


class ProjectUsers(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        "Projects",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(Users, on_delete=models.RESTRICT)
    is_owner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    permissions = models.ManyToManyField(
        Permission,
        through="ProjectUserPermissions",
        verbose_name="project_user_permissions",
    )
    groups = models.ManyToManyField(
        Group,
        through="ProjectUserPermissionGroups",
        verbose_name="project_user_permission_groups",
    )

    class Meta:
        unique_together = (("project", "user"),)
        db_table = "todo_project_users"


class ProjectUserPermissions(models.Model):
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        db_index=False,
    )
    project_user = models.ForeignKey(ProjectUsers, on_delete=models.CASCADE)
    restrict = models.BooleanField(default=False)

    class Meta:
        unique_together = (("project_user", "permission"),)
        db_table = "todo_project_user_permissions"


class ProjectUserPermissionGroups(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        db_index=False,
    )
    project_user = models.ForeignKey(ProjectUsers, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("group", "project_user"),)
        db_table = "todo_project_user_permission_groups"


class Projects(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=256)

    creator_user = models.ForeignKey(
        Users,
        on_delete=models.RESTRICT,
        db_index=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class TaskStatus(StrEnum):
    CREATED = "CREATED"
    PREPARING = "PREPARING"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TaskAssignees(models.Model):
    task = models.ForeignKey("Tasks", on_delete=models.CASCADE)
    project_user = models.ForeignKey(ProjectUsers, on_delete=models.RESTRICT)

    class Meta:
        unique_together = (("project_user", "task"),)
        db_table = "todo_task_assignees"


class Tasks(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)

    reminder_task_id = models.CharField(max_length=255, blank=True, null=True)
    notification_sent = models.BooleanField(default=False)
    status = models.CharField(choices=TaskStatus.choices(), max_length=20)
    title = models.CharField(max_length=256)
    body = models.TextField(null=True, blank=True)

    finished_user = models.ForeignKey(
        Users,
        on_delete=models.RESTRICT,
        related_name="finished_tasks",
        null=True,
        blank=True,
        db_index=False,
    )
    creator_user = models.ForeignKey(
        Users,
        on_delete=models.RESTRICT,
        related_name="created_tasks",
        db_index=False,
    )

    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    assignees = models.ManyToManyField(
        "ProjectUsers",
        through=TaskAssignees,
        through_fields=("task", "project_user"),
    )

    class Meta:
        indexes = [
            BTreeIndex(fields=("project", "status")),
            BTreeIndex(fields=("project", "created_at")),
            BTreeIndex(fields=("project", "title")),
        ]
