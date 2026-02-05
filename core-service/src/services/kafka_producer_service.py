import json
import logging
from enum import StrEnum

from django.conf import settings
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

from helpers.retry_decorator import retry

logger = logging.getLogger(__name__)


class ModelEventsType(StrEnum):
    UserCreated = "user.create"
    UserEnteredProject = "project_user.create"
    ProjectCreated = "project.create"
    ProjectDeleted = "project.delete"
    TaskCreated = "task.create"
    TaskUpdated = "task.update"
    TaskDeleted = "task.delete"


class KafkaProducerService:
    def __init__(self):
        self.__kafka_producer: KafkaProducer | None = None
        self._kafka_settings = dict(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        )

    @property
    def _kafka_producer(self) -> KafkaProducer:
        if (
            self.__kafka_producer is None
            or not self.__kafka_producer.bootstrap_connected()
        ):
            if self.__kafka_producer is not None:
                self.__kafka_producer.close(timeout=1)
            self.__kafka_producer = KafkaProducer(
                **self._kafka_settings,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: str(k).encode("utf-8")
            )
        return self.__kafka_producer

    @retry((KafkaTimeoutError, AssertionError), total_tries=2, logger=logger)
    def send_model_event(
        self, event_type: ModelEventsType, object_id: str, object_data: dict
    ):
        event_payload = {
            "type": event_type,
            "object": object_data,
        }
        self._kafka_producer.send(
            topic=settings.KAFKA_MODEL_EVENTS_TOPIC,
            value=event_payload,
            key=object_id,
        )
        self._kafka_producer.flush()
