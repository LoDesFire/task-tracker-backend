from rest_framework import serializers

from apps.todo.models import ProjectUsers, Tasks


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        exclude = ("assignees", "notification_sent", "reminder_task_id")
        read_only_fields = (
            "id",
            "project",
            "creator_user",
            "created_at",
            "finished_user",
            "finished_at",
            "status",
        )


class TaskChangeSerializer(serializers.ModelSerializer):
    assigned_users = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = self.context.get("project", None)
        if project is None:
            raise serializers.ValidationError("Project context is required.")

        self.project_users = ProjectUsers.objects.filter(
            project=project,
        ).select_related("user")

    def validate_assigned_users(self, values):
        for value in values:
            if not self.project_users.filter(user__id=value).exists():
                raise serializers.ValidationError(
                    f"User {value} is not in the project."
                )
        return values

    def validate_finished_user(self, value):
        if not self.project_users.filter(user=value).exists():
            raise serializers.ValidationError(f"User {value.id} is not in the project.")
        return value

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        assigned_users_uuids = data.get("assigned_users", None)
        if assigned_users_uuids is not None:
            project_users = self.project_users.filter(user__id__in=assigned_users_uuids)
            if set(project_users) != set(assigned_users_uuids):
                raise serializers.ValidationError("Invalid or unassigned users")
            ret["assignees"] = project_users

        return ret

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop("assignees")
        ret["assigned_users"] = [
            str(project_user.user_id) for project_user in instance.assignees.all()
        ]
        return ret

    class Meta:
        model = Tasks
        exclude = ("notification_sent", "reminder_task_id")
        read_only_fields = (
            "id",
            "project",
            "creator_user",
            "created_at",
        )
