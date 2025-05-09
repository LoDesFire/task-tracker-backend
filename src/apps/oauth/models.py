import uuid

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
        user.groups.add(Group.objects.get(name="Users"))

        return user

    def get_by_natural_key(self, username):
        raise Exception("Not implemented")


class Users(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    is_verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
        default_permissions = ()
        permissions = ()
