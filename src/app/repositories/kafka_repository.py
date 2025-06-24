import json
from typing import Callable, Coroutine

from aiokafka import AIOKafkaProducer

from src.constants import KafkaUserEventTypes
from src.schemas.kafka_schemas import UserInfoSchema
from src.settings.general_settings import settings


class KafkaRepository:
    def __init__(
        self,
        kafka_producer_factory: Callable[[], Coroutine[None, None, AIOKafkaProducer]],
    ):
        self.kafka_producer_factory = kafka_producer_factory

    async def produce_user_event(
        self, event_type: KafkaUserEventTypes, user_info: UserInfoSchema
    ):
        message_json = {
            "event_type": event_type,
            "user": user_info.model_dump(),
        }
        raw_message = json.dumps(message_json).encode("utf-8")
        producer = await self.kafka_producer_factory()
        await producer.send(
            topic=settings.kafka_settings.user_events_topic,
            value=raw_message,
        )
        await producer.stop()
