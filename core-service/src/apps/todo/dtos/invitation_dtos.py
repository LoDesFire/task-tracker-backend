from dataclasses import dataclass

from django.contrib.auth.models import Group, Permission

from apps.todo.models import Projects


@dataclass(frozen=True)
class InvitationDto:
    project: Projects
    permissions: list[Permission]
    restricted_permissions: list[Permission]
    permission_groups: list[Group]
    emails: list[str] | None

    def __serialize(self, obj):
        if isinstance(obj, Projects):
            return obj.id
        elif isinstance(obj, Permission):
            return f"{obj.content_type.app_label}.{obj.codename}"
        elif isinstance(obj, Group):
            return obj.name
        elif isinstance(obj, list):
            return [self.__serialize(item) for item in obj]
        else:
            return obj

    @property
    def dict(self):
        return {k: self.__serialize(v) for k, v in self.__dict__.items()}
