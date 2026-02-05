from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db.models import Q
from rest_framework import serializers

from apps.oauth.models import GroupPermissionsScope


class GroupField(serializers.RelatedField):
    def __init__(self, group_scope: GroupPermissionsScope | None = None, **kwargs):
        self.group_scope = group_scope
        super().__init__(**kwargs)

    def _get_groups(self):
        cache_key = f"groups:{self.group_scope or ''}"
        groups = cache.get(cache_key)
        if groups is None:
            queryset = self.get_queryset()
            groups = {group.name: group for group in queryset}
            cache.set(cache_key, groups, timeout=3600)
        return groups

    def get_queryset(self):
        query = Q()
        if self.group_scope:
            query &= Q(groupscope__scope=self.group_scope)
        return Group.objects.filter(query)

    def to_representation(self, value: Group):
        return value.name

    def to_internal_value(self, data):
        groups = self._get_groups()
        try:
            return groups[data]
        except KeyError:
            raise serializers.ValidationError(
                "Invalid group string ({}) or group does not exist.".format(data),
            )
