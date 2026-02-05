import logging

from django.core.exceptions import ObjectDoesNotExist

from apps.todo.models import TaskAssignees
from apps.todo.tasks import (
    send_deadline_notification_batch_emails,
    send_status_changing_batch_emails,
)
from services import RedisService

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service

    def subscribe_on_task_statuses(self, user_id: str, task_id: int):
        return self.redis_service.subscribe_user_on_task_statuses(task_id, user_id)

    def unsubscribe_on_task_statuses(self, user_id: str, task_id: int):
        return self.redis_service.unsubscribe_user_on_task_statuses(task_id, user_id)

    def send_task_statuses_notification(self, task_id: int):
        subscribed_user_ids = self.redis_service.get_subscribed_users_on_task_statuses(
            task_id
        )
        if subscribed_user_ids is None:
            return
        else:
            subscribed_user_ids = set(subscribed_user_ids)
        task_assignees = TaskAssignees.objects.filter(task_id=task_id).select_related(
            "project_user__user", "project_user__user__usersinfo"
        )
        assigned_user_emails = []
        for assignee in task_assignees:
            try:
                if str(assignee.project_user.user.id) in subscribed_user_ids:
                    assigned_user_emails.append(
                        assignee.project_user.user.usersinfo.email
                    )
            except ObjectDoesNotExist:
                continue

        send_status_changing_batch_emails.delay(
            *assigned_user_emails,
            task_id=task_id,
        )

    def cancel_deadline_notification(self, celery_task_id: str):
        send_deadline_notification_batch_emails.AsyncResult(celery_task_id).revoke()
