import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery()
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "create-deadline-notification-tasks-every-five-minutes": {
        "task": "apps.todo.tasks.check_pending_reminders",
        "schedule": crontab(minute="*/5"),
    }
}
