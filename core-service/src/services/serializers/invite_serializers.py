import datetime

from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import PrimaryKeyRelatedField

from apps.oauth.models import GroupName, GroupPermissionsScope
from apps.todo.fields.group_field import GroupField
from apps.todo.fields.permission_field import PermissionField
from apps.todo.models import Projects


class InvitationLinkInputSerializer(serializers.Serializer):
    permissions = PermissionField(
        permission_group_name=GroupName.PROJECT_ALL,
        required=True,
        many=True,
    )
    permission_groups = GroupField(
        group_scope=GroupPermissionsScope.PROJECT,
        many=True,
        required=True,
    )
    emails = serializers.ListField(
        child=serializers.CharField(max_length=255, validators=[EmailValidator()]),
        required=False,
        default=None,
    )
    expires_in = serializers.DurationField(
        required=False,
        default=datetime.timedelta(hours=24),
        min_value=datetime.timedelta(minutes=60),
    )

    def validate_permissions(self, value):
        allowed_permissions = self.context.get("allowed_permissions", None)
        if allowed_permissions is None:
            return value

        permissions = self.initial_data.get("permissions", [])
        for perm in permissions:
            if perm not in allowed_permissions:
                raise ValidationError(detail=f'Restricted permission "{perm}".')

        return value

    def validate_permission_groups(self, value):
        allowed_groups = self.context.get("allowed_groups", None)
        if allowed_groups is None:
            return value

        permission_groups = self.initial_data.get("permission_groups", [])
        for group in permission_groups:
            if group not in allowed_groups:
                raise ValidationError(detail=f'Restricted group "{group}".')

        return value

    def validate_emails(self, value):
        if value is None:
            return value
        if len(value) != len(set(value)):
            raise serializers.ValidationError(detail="Email addresses are not unique.")
        return value


class InvitationAcceptSerializer(serializers.Serializer):
    invitation_id = serializers.UUIDField(
        required=True,
    )


class InvitationInfoSerializer(serializers.Serializer):
    project = PrimaryKeyRelatedField(
        queryset=Projects.objects.all(),
        required=True,
    )
    permissions = PermissionField(
        permission_group_name=GroupName.PROJECT_ALL,
        required=True,
        many=True,
    )
    restricted_permissions = PermissionField(
        permission_group_name=GroupName.PROJECT_ALL,
        required=False,
        many=True,
    )
    permission_groups = GroupField(
        group_scope=GroupPermissionsScope.PROJECT,
        many=True,
        required=True,
    )
    emails = serializers.ListField(
        child=serializers.CharField(max_length=255, validators=[EmailValidator()]),
        required=False,
        allow_null=True,
        default=None,
    )
