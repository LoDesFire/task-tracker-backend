import logging
from datetime import datetime, timedelta, timezone

from celery import Task, shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from apps.todo.models import TaskAssignees, Tasks
from apps.todo.services.ses_service import SESService
from helpers.exceptions import SESEmailsSendingExceptions

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_invitation_batch_emails(self: Task, *emails: str, invitation_id: str):
    try:
        ses_service = SESService(settings.AWS_SES_SENDER_EMAIL)
        return ses_service.send_invitation_batch_emails(
            *emails,
            invitation_id=invitation_id,
        )
    except SESEmailsSendingExceptions as exc:
        return self.retry(
            args=emails[exc.sent_emails_count:],
            kwargs=dict(invitation_id=invitation_id),
            countdown=2 ** self.request.retries,
            exc=exc,
        )


@shared_task(bind=True, max_retries=3)
def send_deadline_notification_batch_emails(self: Task, task_id):
    assignees = TaskAssignees.objects.filter(task_id=task_id).select_related(
        "project_user__user__usersinfo"
    )
    emails = []
    for assignee in assignees:
        try:
            emails.append(assignee.project_user.user.usersinfo.email)
        except ObjectDoesNotExist:
            pass

    task = Tasks.objects.filter(id=task_id).select_related("project").first()

    try:
        ses_service = SESService(settings.AWS_SES_SENDER_EMAIL)
        ses_service.send_deadline_batch_emails(
            *emails,
            deadline=task.deadline,
            task_title=task.title,
            project_title=task.project.title,
        )

        task.reminder_task_id = None
        task.notification_sent = True
        task.save()
    except SESEmailsSendingExceptions as exc:
        self.retry(
            args=emails[exc.sent_emails_count:],
            kwargs=dict(task_id=task_id),
            countdown=2 ** self.request.retries,
            exc=exc,
        )


@shared_task(bind=True, max_retries=3)
def send_status_changing_batch_emails(
        self,
        *emails: str,
        task_id,
):
    task = Tasks.objects.filter(id=task_id).select_related("project").first()
    try:
        ses_service = SESService(settings.AWS_SES_SENDER_EMAIL)
        return ses_service.send_status_changing_batch_emails(
            *emails,
            new_status=task.status,
            task_title=task.title,
            project_title=task.project.title,
        )
    except SESEmailsSendingExceptions as exc:
        return self.retry(
            args=emails[exc.sent_emails_count:],
            kwargs=dict(task_id=task_id),
            countdown=2 ** self.request.retries,
            exc=exc,
        )


@shared_task
def check_pending_reminders():
    now = datetime.now(timezone.utc)

    tasks = Tasks.objects.filter(
        deadline__gte=now + timedelta(minutes=1),
        deadline__lte=now + timedelta(minutes=70),
        notification_sent=False,
        reminder_task_id=None,
    )

    for task in tasks:
        reminder_time = task.deadline - timedelta(hours=1)

        if task.reminder_task_id:
            send_deadline_notification_batch_emails.AsyncResult(
                task.reminder_task_id
            ).revoke()

        result = send_deadline_notification_batch_emails.apply_async(
            args=[task.id],
            eta=reminder_time,
        )
        task.reminder_task_id = result.id
        task.save()
