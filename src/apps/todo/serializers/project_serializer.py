from rest_framework import serializers

from apps.todo.models import Projects
from helpers.exceptions import InternalException


class ProjectSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField(method_name="get_users")
    users_count = serializers.SerializerMethodField(method_name="get_users_count")

    def __init__(self, *args, **kwargs):
        context: dict = kwargs["context"]
        super().__init__(*args, **kwargs)

        if context.get("detailed", False):
            self.fields.pop("users_count")
        else:
            self.fields.pop("users")

    @staticmethod
    def get_users(obj):
        if not hasattr(obj, "projectusers_set"):
            raise InternalException("There is no project users set")
        user_ids = [proj_user.user.id for proj_user in obj.projectusers_set.all()]
        return user_ids

    @staticmethod
    def get_users_count(obj):
        if not hasattr(obj, "users_count"):
            raise InternalException("There is no users count field")
        return obj.users_count

    class Meta:
        model = Projects
        fields = "__all__"
        read_only_fields = ("id", "creator_user", "created_at", "users_count", "users")
