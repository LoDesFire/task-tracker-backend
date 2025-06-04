from typing import Literal
from uuid import UUID

import jwt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission
from django.db.models import ManyToManyField
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from apps.oauth.dataclasses import JWTToken
from apps.todo.models import Projects, ProjectUsers

UserModel = get_user_model()


class AuthorizationBackend(BaseBackend):
    def authenticate(self, request, *args, **kwargs): ...

    def get_user(self, *args, **kwargs): ...

    @staticmethod
    def _get_user_permissions(user_obj, restricted=False):
        return Permission.objects.filter(
            userpermissions__restrict=restricted,
            userpermissions__user=user_obj,
        )

    def _get_group_permissions(self, user_obj):
        restricted_permission_ids = self._get_user_permissions(
            user_obj,
            restricted=True,
        )
        user_groups_field = UserModel._meta.get_field("groups")
        if not isinstance(user_groups_field, ManyToManyField):
            raise Exception(f"{user_groups_field} is not a ManyToManyField")
        user_groups_query = f"group__{user_groups_field.related_query_name()}"
        return Permission.objects.filter(**{user_groups_query: user_obj}).exclude(
            pk__in=restricted_permission_ids,
        )

    @staticmethod
    def _get_users_project_permissions(project_user_obj, restricted=False):
        return Permission.objects.filter(
            projectuserpermissions__project_user=project_user_obj,
            projectuserpermissions__restrict=restricted,
        )

    def _get_group_project_permissions(self, project_user_obj):
        restricted_permission_ids = self._get_users_project_permissions(
            project_user_obj,
            restricted=True,
        )
        user_groups_field = ProjectUsers._meta.get_field("groups")
        if not isinstance(user_groups_field, ManyToManyField):
            raise Exception(f"{user_groups_field} is not a ManyToManyField")
        user_groups_query = f"group__{user_groups_field.related_query_name()}"
        return Permission.objects.filter(
            **{user_groups_query: project_user_obj}
        ).exclude(
            pk__in=restricted_permission_ids,
        )

    def _get_project_permissions(
        self,
        user_obj,
        project_obj,
        from_name: Literal["user", "group"],
    ) -> set[Permission]:
        perm_cache_name = "_%s_project_perm_cache" % from_name

        if not hasattr(user_obj, perm_cache_name):
            project_user_obj = ProjectUsers.objects.get(
                project=project_obj, user=user_obj
            )
            if not project_user_obj.is_active:
                return set()
            if project_user_obj.is_owner:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, "_get_%s_project_permissions" % from_name)(
                    project_user_obj
                )

            perms = perms.values_list("content_type__app_label", "codename").order_by()
            setattr(
                user_obj,
                perm_cache_name,
                {"%s.%s" % (ct, name) for ct, name in perms},
            )

        return getattr(user_obj, perm_cache_name)

    def _get_permissions(
        self,
        user_obj,
        from_name: Literal["group", "user"],
    ) -> set[Permission]:
        perm_cache_name = "_%s_perm_cache" % from_name

        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, "_get_%s_permissions" % from_name)(user_obj)

            perms = perms.values_list("content_type__app_label", "codename").order_by()
            setattr(
                user_obj,
                perm_cache_name,
                {"%s.%s" % (ct, name) for ct, name in perms},
            )

        return getattr(user_obj, perm_cache_name)

    def get_group_permissions(self, user_obj, obj=None):
        if obj is None:
            return self._get_permissions(user_obj, "group")

        if isinstance(obj, Projects):
            return self._get_project_permissions(user_obj, obj, "group")

    def get_user_permissions(self, user_obj, obj=None):
        if obj is None:
            return self._get_permissions(user_obj, "user")

        if isinstance(obj, Projects):
            return self._get_project_permissions(user_obj, obj, "user")

    def get_all_permissions(self, user_obj, obj=None):
        cache_key = "_perm_cache_{}".format(obj.__class__.__name__) if obj else "_perm_cache_global"
        if not hasattr(user_obj, cache_key):
            setattr(user_obj, cache_key, super().get_all_permissions(user_obj, obj))
        return getattr(user_obj, cache_key)

    def has_perm(self, user_obj, perm, obj=None):
        return perm in self.get_all_permissions(user_obj, obj=obj)


class OAuth2Backend(BaseBackend):
    def authenticate(self, request, **kwargs):
        token: JWTToken = kwargs.get("token")
        decoded_token = self.__decode_token(token)

        if decoded_token is None:
            return None

        try:
            user = UserModel._default_manager.get_and_update_with_jwt(decoded_token)
        except UserModel.DoesNotExist:
            user = UserModel._default_manager.create_from_jwt(decoded_token)

        return user

    def get_user(self, user_id: UUID):
        try:
            user = UserModel._default_manager.get_by_id(user_id)
        except UserModel.DoesNotExist:
            return None
        return user

    @staticmethod
    def __decode_token(raw_token) -> JWTToken | None:
        try:
            decoded_token = jwt.decode(
                raw_token,
                options=dict(
                    require=["exp", "iat", "app_id", "jwt_id", "nbf", "sub", "type"],
                    verify_iat=True,
                    verify_nbf=True,
                    verify_exp=True,
                ),
                key=settings.JWT_PUBLIC_KEY,
                algorithms=["RS256"],
            )
            if decoded_token["type"] != "access":
                return None
        except jwt.InvalidTokenError:
            return None

        return JWTToken.from_dict(decoded_token)


class DjangoOAuthBackend(OAuth2Backend, AuthorizationBackend):
    """DjangoOAuthBackend"""


class OAuth2Authentication(BaseAuthentication):
    def authenticate(self, request):
        raw_token = get_authorization_header(request).decode("utf-8")

        if raw_token is None:
            return None

        user = authenticate(request=request, token=raw_token.removeprefix("Bearer "))
        if user and user.is_active:
            return user, None

    def authenticate_header(self, request):
        return "Bearer"
