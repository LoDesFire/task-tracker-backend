from rest_framework import serializers

from apps.oauth.models import GroupName, GroupPermissionsScope, Users
from apps.todo.fields.group_field import GroupField
from apps.todo.fields.permission_field import PermissionField


class ProjectUserIDSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.none(),
        required=False,
        allow_null=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = self.context.get("project", None)
        self.fields["user_id"].queryset = Users.objects.filter(
            projectusers__project=project,
        ).all()


class ProjectPermissionsSerializer(serializers.Serializer):
    allowed = PermissionField(
        permission_group_name=GroupName.PROJECT_ALL,
        many=True,
    )
    restricted = PermissionField(
        permission_group_name=GroupName.PROJECT_ALL,
        many=True,
    )


class ProjectPermissionsChangeSerializer(serializers.Serializer):
    permissions = ProjectPermissionsSerializer()
    groups = GroupField(
        group_scope=GroupPermissionsScope.PROJECT,
        many=True,
    )

    def validate(self, attrs):
        allowed_set = set(attrs["permissions"]["allowed"])
        restricted_set = set(attrs["permissions"]["restricted"])

        if len(allowed_set.intersection(restricted_set)) > 0:
            raise serializers.ValidationError(
                "Allowed and restricted permissions must be different"
            )
        return attrs
