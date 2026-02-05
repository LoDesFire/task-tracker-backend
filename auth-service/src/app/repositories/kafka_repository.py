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
            "type": event_type,
            "object": user_info.model_dump(),
        }
        producer = await self.kafka_producer_factory()
        await producer.send(
            topic=settings.kafka_settings.user_events_topic,
            value=message_json,
            key=user_info.id,
        )
        await producer.stop()
