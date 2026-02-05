import json
import logging
from json import JSONDecodeError

from aiokafka import AIOKafkaConsumer, TopicPartition, ConsumerRecord
from kafka_consumer.handlers import handle_kafka_model_event
from settings import settings

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self,
    ):
        self.kafka_consumer = AIOKafkaConsumer(
            settings.kafka_settings.model_events_topic,
            bootstrap_servers=settings.kafka_settings.bootstrap_servers,
            group_id=settings.kafka_settings.consumer_group_id,
            value_deserializer=self._message_deserializer,
            enable_auto_commit=False,
            auto_offset_reset='earliest',
        )

    @staticmethod
    def _message_deserializer(raw_message: bytes) -> dict | None:
        try:
            return json.loads(raw_message.decode("utf-8"))
        except (JSONDecodeError, ValueError):
            logger.warning("Failed to deserialize message: %s", raw_message)
            return None

    async def consume(self):
        try:
            await self.kafka_consumer.start()
            async for message in self.kafka_consumer:
                await self.handle_kafka_message(message)
                tp = TopicPartition(message.topic, message.partition)
                await self.kafka_consumer.commit(offsets={tp: message.offset + 1})
        finally:
            await self.kafka_consumer.stop()

    @staticmethod
    async def handle_kafka_message(message: ConsumerRecord):
        if message.value is None:
            return None
        try:
            match message.topic:
                case settings.kafka_settings.model_events_topic:
                    await handle_kafka_model_event(message.value, message.key.decode("utf-8"))
        except Exception as e:
            logger.warning("Failed to handle message: %s. Error: %s", message, e)
            pass
