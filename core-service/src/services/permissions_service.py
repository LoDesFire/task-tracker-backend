import datetime
from collections import defaultdict

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.cache import cache
from django.db.models import Q

from apps.oauth.models import GroupName, GroupPermissionsScope, GroupScope
from apps.todo.models import ProjectUsers


class PermissionsService:
    permissions_group_tree_cache_key = "permissions_group_expanded_tree"
    permissions_group_cache_timeout_minutes = 0 if settings.DEBUG else 2

    @classmethod
    def __get_child_group_ids(cls, permissions_group_id):
        cached_tree = cache.get(cls.permissions_group_tree_cache_key, None)
        if cached_tree is None:
            # Transform group relations into the tree in dictionary
            groups = GroupScope.objects.values_list("group_id", "parent__group_id")
            groups_tree = defaultdict(list)
            for group, parent in groups:
                groups_tree[parent].append(group)

            # Expand the tree (find all children for the nodes)
            cached_tree = {}

            def recursive_traversal(nodes):
                all_nodes = set()
                for node in nodes:
                    child_nodes = recursive_traversal(groups_tree[node])
                    cached_tree[node] = child_nodes
                    all_nodes.update(child_nodes.union({node}))
                return all_nodes

            # start expanding from the root node
            recursive_traversal(groups_tree[None])

            cache.set(
                key=cls.permissions_group_tree_cache_key,
                value=cached_tree,
                timeout=datetime.timedelta(
                    minutes=cls.permissions_group_cache_timeout_minutes,
                ).total_seconds(),
            )

        return cached_tree.get(
            permissions_group_id,
            set(),
        ).union({permissions_group_id})

    @staticmethod
    def permissions_to_repr(permissions_queryset):
        permissions = permissions_queryset.values_list(
            "content_type__app_label", "codename"
        ).order_by("content_type__model")
        return [f"{label}.{codename}" for label, codename in permissions]

    @classmethod
    def get_available_groups_queryset(cls, user, project=None):
        if project is None:
            if user.is_superuser:
                groups = Group.objects.filter(
                    groupscope__scope=GroupPermissionsScope.GLOBAL,
                )
            else:
                groups = Group.objects.filter(
                    user=user,
                    groupscope__scope=GroupPermissionsScope.GLOBAL,
                )
        else:
            if user.is_superuser:
                groups = Group.objects.filter(
                    groupscope__scope=GroupPermissionsScope.PROJECT,
                )
            else:
                groups = Group.objects.filter(
                    groupscope__scope=GroupPermissionsScope.PROJECT,
                    projectusers__user=user,
                    projectusers__project=project,
                )

        available_group_ids = set()
        for group in groups:
            available_group_ids.update(cls.__get_child_group_ids(group.pk))

        available_groups = Group.objects.filter(
            id__in=available_group_ids,
        )
        return available_groups

    @classmethod
    def get_available_group_permissions(
        cls, user, project=None
    ) -> list[dict[str, list]]:
        groups = cls.get_available_groups_queryset(user, project).prefetch_related(
            "permissions",
        )

        group_permissions = [
            {
                "group_name": group.name,
                "permissions": cls.permissions_to_repr(group.permissions),
            }
            for group in groups
        ]
        return group_permissions

    @classmethod
    def get_available_permissions_queryset(cls, user, project=None):
        if project is None:
            if user.is_superuser:
                permissions_queryset = Permission.objects.filter(
                    group__name=GroupName.ALL,
                )
            else:
                permissions_queryset = Permission.objects.filter(
                    user=user,
                    userpermissions__restrict=False,
                )
        else:
            if user.is_superuser:
                permissions_queryset = Permission.objects.filter(
                    group__name=GroupName.PROJECT_ALL,
                )
            else:
                project_user = ProjectUsers.objects.get(
                    user=user,
                    project=project,
                )
                if project_user.is_owner:
                    permissions_queryset = Permission.objects.filter(
                        group__name=GroupName.PROJECT_ALL,
                    )
                else:
                    permissions_queryset = Permission.objects.filter(
                        projectuserpermissions__project_user=project_user,
                        projectuserpermissions__restrict=False,
                    )
        return permissions_queryset

    @classmethod
    def get_available_permissions(cls, user, project=None):
        return cls.permissions_to_repr(
            cls.get_available_permissions_queryset(user, project)
        )

    @classmethod
    def get_restricted_permissions_queryset(cls, user, project=None):
        if project is None:
            if user.is_superuser:
                permissions_queryset = Permission.objects.none()
            else:
                permissions_queryset = Permission.objects.filter(
                    user=user,
                    userpermissions__restrict=True,
                )
        else:
            if user.is_superuser:
                permissions_queryset = Permission.objects.none()
            else:
                project_user = ProjectUsers.objects.get(
                    user=user,
                    project=project,
                )
                if project_user.is_owner:
                    return Permission.objects.none()
                permissions_queryset = Permission.objects.filter(
                    projectuserpermissions__project_user=project_user,
                    projectuserpermissions__restrict=True,
                )
        return permissions_queryset

    @classmethod
    def get_restricted_permissions(cls, user, project=None):
        return cls.permissions_to_repr(
            cls.get_restricted_permissions_queryset(user, project)
        )

    @staticmethod
    def is_project_groups_available_for_user(project, user, groups: list[Group]):
        available_groups_set = set(
            PermissionsService.get_available_groups_queryset(user, project)
        )

        return set(groups).issubset(available_groups_set)

    @staticmethod
    def is_project_permissions_available_for_user(
        project, user, permissions: list[Permission]
    ):
        available_permissions = map(
            lambda p: str(p).split("."), user.get_all_permissions(obj=project)
        )
        query = Q()
        for app_label, codename in available_permissions:
            query |= Q(content_type__app_label=app_label, codename=codename)

        available_permissions_set = set(Permission.objects.filter(query))

        return set(permissions).issubset(available_permissions_set)
