import datetime
import logging
import uuid

from django.conf import settings
from django.contrib.auth.models import User

from apps.todo.dtos.invitation_dtos import InvitationDto
from apps.todo.models import Projects
from apps.todo.tasks import send_invitation_batch_emails
from services.permissions_service import PermissionsService
from services.redis_service import RedisService
from services.serializers.invite_serializers import (
    InvitationAcceptSerializer,
    InvitationInfoSerializer,
    InvitationLinkInputSerializer,
)

logger = logging.getLogger(__name__)


class InvitationService:
    @classmethod
    def create_invitation(
        cls,
        user: User,
        project: Projects,
        invitation_data,
    ):
        available_permissions = PermissionsService.get_available_permissions(
            user,
            project,
        )
        available_groups = PermissionsService.get_available_groups_queryset(
            user,
            project,
        ).values_list("name", flat=True)
        invitation_serializer = InvitationLinkInputSerializer(
            data=invitation_data,
            context={
                "allowed_permissions": available_permissions,
                "allowed_groups": available_groups,
            },
        )
        invitation_serializer.is_valid(raise_exception=True)

        invitation_id = uuid.uuid4()
        expires_at = (
            datetime.datetime.now(tz=datetime.timezone.utc)
            + invitation_serializer.validated_data["expires_in"]
        )

        invite_info = InvitationDto(
            project=project,
            restricted_permissions=PermissionsService.get_restricted_permissions(
                user,
                project,
            ),
            permissions=invitation_serializer.validated_data["permissions"],
            permission_groups=invitation_serializer.validated_data["permission_groups"],
            emails=invitation_serializer.validated_data["emails"],
        )

        RedisService().save_invite_link_info(
            invitation_id=invitation_id,
            expires_at=expires_at,
            invitation_dict=invite_info.dict,
        )

        return {
            "invitation_id": invitation_id,
            "emails": invite_info.emails,
            "expires_at": expires_at,
        }

    @classmethod
    def get_invitation(cls, invitation_data):
        invitation_accept = InvitationAcceptSerializer(data=invitation_data)
        invitation_accept.is_valid(raise_exception=True)

        invitation_id = invitation_accept.validated_data["invitation_id"]
        invitation_dict = RedisService().get_invite_link_info(invitation_id)
        invite_info_serializer = InvitationInfoSerializer(data=invitation_dict)
        if not invite_info_serializer.is_valid():
            logger.warning(
                "Invitation validation errors:\n%s",
                str(
                    invite_info_serializer.errors
                    if invite_info_serializer
                    else "None object"
                ),
            )
            return None

        return invite_info_serializer.validated_data

    @staticmethod
    def send_invitation_emails(*destination_emails, invitation_id: str):
        for slice_idx in range(
            0, len(destination_emails), settings.AWS_SES_MAX_RECIPIENTS_PER_MESSAGE
        ):
            sliced_emails = destination_emails[
                slice_idx : slice_idx + settings.AWS_SES_MAX_RECIPIENTS_PER_MESSAGE
            ]
            send_invitation_batch_emails.delay(
                *sliced_emails,
                invitation_id=invitation_id,
            )
