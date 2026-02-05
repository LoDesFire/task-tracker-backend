from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.db.models import Q
from rest_framework import serializers


class PermissionField(serializers.RelatedField):
    permissions_cache_timeout = 0 if settings.DEBUG else 5

    def __init__(self, permission_group_name: str | None = None, **kwargs):
        self.permission_group = permission_group_name
        super().__init__(**kwargs)

    def _get_permissions(self):
        cache_key = f"permissions_{self.permission_group.replace(' ', '-') or ''}"
        permissions = cache.get(cache_key)
        if permissions is None:
            queryset = self.get_queryset().select_related("content_type")
            permissions = {
                f"{perm.content_type.app_label}.{perm.codename}": perm
                for perm in queryset
            }
            cache.set(cache_key, permissions, timeout=self.permissions_cache_timeout)
        return permissions

    def get_queryset(self):
        query = Q()
        if self.permission_group:
            query &= Q(group__name=self.permission_group)
        return Permission.objects.filter(query)

    def to_representation(self, value: Permission):
        return f"{value.content_type.app_label}.{value.codename}"

    def to_internal_value(self, data):
        permissions = self._get_permissions()
        try:
            return permissions[data]
        except KeyError:
            raise serializers.ValidationError(
                "Invalid permission string ({}) or permission does not exist.".format(
                    data,
                ),
            )
