import asyncio

from aiokafka import AIOKafkaProducer

from src.settings.general_settings import settings


class KafkaProducerDependency:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._producer: AIOKafkaProducer | None = None
        self._bootstrap_servers = settings.kafka_settings.bootstrap_servers

    async def get_producer(self) -> AIOKafkaProducer:
        """Initialize and return the producer if not already created."""
        async with self._lock:
            if self._producer is None:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self._bootstrap_servers
                )

        await self._producer.start()
        return self._producer

    @classmethod
    async def stop_producer(cls):
        """Stop the producer if it exists."""
        producer_dep: KafkaProducerDependency = cls._instance
        if producer_dep._producer is not None:
            await producer_dep._producer.stop()
            producer_dep._producer = None
