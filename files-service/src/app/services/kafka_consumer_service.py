# import asyncio
# import json
# import logging
# from json import JSONDecodeError
#
# from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord, TopicPartition
#
# from src.settings.general_settings import settings
# # from src.web.kafka import handlers
# # from src.web.kafka.schemas import UserRequestSchema
#
# logger = logging.getLogger(__name__)
#
#
# class KafkaConsumerService:
#     _instance = None
#
#     def __new__(cls, *args, **kwargs):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def __init__(
#             self,
#             user_repository: UserRepository,
#     ):
#         self.user_repository = user_repository
#         self.kafka_consumer = AIOKafkaConsumer(
#             settings.kafka_settings.users_consumer_topic,
#             bootstrap_servers=settings.kafka_settings.bootstrap_servers,
#             group_id=settings.kafka_settings.users_consumer_group_id,
#             value_deserializer=self._message_deserializer,
#             enable_auto_commit=False,
#             auto_offset_reset='earliest',
#         )
#
#     @staticmethod
#     def _message_deserializer(raw_message: bytes) -> dict | None:
#         try:
#             return json.loads(raw_message.decode("utf-8"))
#         except (JSONDecodeError, ValueError):
#             logger.warning("Failed to deserialize message: %s", raw_message)
#             return None
#
#     async def consume(self):
#
#         async for message in self.kafka_consumer:
#             await self.handle_kafka_message(message)
#             tp = TopicPartition(message.topic, message.partition)
#             await self.kafka_consumer.commit(offsets={tp: message.offset + 1})
#
#     async def start(self):
#         await self.kafka_consumer.start()
#         asyncio.create_task(self.consume())
#
#     async def stop(self):
#         await self.kafka_consumer.stop()
#
#     async def handle_kafka_message(self, message: ConsumerRecord):
#         if message.value is None:
#             return None
#         try:
#             match message.topic:
#                 case settings.kafka_settings.users_consumer_topic:
#                     await handlers.users_request_handler(
#                         kafka_producer=await self._kafka_producer_factory(),
#                         user_repository=self.user_repository,
#                         user_schema=UserRequestSchema(**message.value)
#                     )
#                 case _:
#                     return None
#         except Exception as e:
#             logger.warning("Failed to handle message: %s. Error: %s", message, e)
#             pass
