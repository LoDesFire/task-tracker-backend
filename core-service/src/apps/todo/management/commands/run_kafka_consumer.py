import json
import logging
import signal

from django.conf import settings
from django.core.management import BaseCommand
from kafka import KafkaConsumer  # type: ignore
from kafka.consumer.fetcher import ConsumerRecord

from apps.oauth.models import Users, UsersInfo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.consumer = None

    def handle_shutdown(self, signum, frame):
        self.stdout.write(self.style.WARNING("Shutting down Kafka consumer..."))
        if self.consumer:
            self.consumer.close()
        self.stdout.write(self.style.SUCCESS("Consumer shut down successfully."))
        exit(0)

    def handle(self, *args, **options):
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            "user_events_topic",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset="latest",
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )

        self.stdout.write(self.style.SUCCESS("Starting Kafka consumer..."))
        try:
            for message in self.consumer:
                try:
                    self.handle_message(message)
                except Exception as e:
                    logger.error("Exception occurred: %s", str(e))
                else:
                    self.stdout.write(self.style.SUCCESS(str(message.value)))
        except KeyboardInterrupt:
            self.handle_shutdown(None, None)
        finally:
            self.consumer.close()

    def handle_message(self, message: ConsumerRecord):
        message_value = message.value
        if message.topic == "user_events_topic":
            user = message_value["user"]
            user_id = user["id"]
            username = user["username"]
            email = user["email"]

            user, _ = Users._default_manager.get_or_create_from_kafka(
                user_id=user_id,
            )

            users_info, is_users_info_created = UsersInfo.objects.get_or_create(
                user=user,
                defaults=dict(
                    username=username,
                    email=email,
                ),
            )

            if not is_users_info_created:
                users_info.username = username
                users_info.email = email

            users_info.save()
