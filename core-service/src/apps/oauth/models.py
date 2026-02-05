import uuid
from enum import StrEnum

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import (
    AbstractBaseUser,
    Group,
    Permission,
    PermissionsMixin,
)
from django.db import models

from apps.oauth.dataclasses import JWTToken


class UsersManager(BaseUserManager):
    """UserManager"""

    def get_by_id(self, user_id: uuid.UUID):
        return self.get(**{"id": user_id})

    def get_and_update_with_jwt(self, decoded_jwt: JWTToken):
        user = self.get(id=decoded_jwt.sub.hex)

        if (
            user.is_verified != decoded_jwt.is_verified
            or user.is_superuser != decoded_jwt.is_admin
        ):
            user.is_verified = decoded_jwt.is_verified
            user.is_superuser = decoded_jwt.is_admin
            user.save()

        return user

    def create_from_jwt(self, decoded_jwt: JWTToken):
        user = self.model()
        user.set_unusable_password()

        user.id = decoded_jwt.sub
        user.is_verified = decoded_jwt.is_verified
        user.is_superuser = decoded_jwt.is_admin
        user.is_active = True
        user.save()
        user.groups.add(Group.objects.get(name=GroupName.USERS), through_defaults={})

        return user

    def get_or_create_from_kafka(self, user_id):
        user, is_created = self.get_or_create(id=user_id)
        user.save()

        if is_created:
            user.groups.add(
                Group.objects.get(name=GroupName.USERS), through_defaults={}
            )
        return user, is_created

    def get_by_natural_key(self, username):
        raise Exception("Not implemented")


class Users(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    is_verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        through="UserGroups",
        verbose_name="user_groups",
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        through="UserPermissions",
        verbose_name="user_permissions",
        related_name="user_set",
        related_query_name="user",
    )

    objects = UsersManager()

    USERNAME_FIELD = "id"


class UserGroups(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        db_index=False,
    )
    user = models.ForeignKey(Users, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("group", "user"),)
        db_table = "oauth_user_groups"


class UserPermissions(models.Model):
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        db_index=False,
    )
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    restrict = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "permission"),)
        db_table = "oauth_user_permissions"


class GroupPermissionsScope(StrEnum):
    ROOT = "ROOT"
    PROJECT = "PROJECT"
    GLOBAL = "GLOBAL"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class GroupName(StrEnum):
    ROOT = "Root"
    USERS = "Users"
    ALL = "All"
    PROJECT_ALL = "Project All"
    PROJECT_MODERATORS = "Project Moderators"
    PROJECT_USERS = "Project Users"

    @classmethod
    def all_names(cls):
        return [(key.value, key.name) for key in cls]


class GroupScope(models.Model):
    scope = models.CharField(
        max_length=50,
        choices=GroupPermissionsScope.choices(),
    )
    parent = models.ForeignKey(
        "GroupScope",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "oauth_group_scope"


class UsersInfo(models.Model):
    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, null=False, unique=True
    )
    username = models.CharField(null=True)
    email = models.EmailField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "oauth_user_info"
