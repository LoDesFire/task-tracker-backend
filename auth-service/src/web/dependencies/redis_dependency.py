import threading
from functools import partial
from typing import Callable

from redis.asyncio import ConnectionPool, Redis

from src.settings.general_settings import settings


class RedisDependency:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(RedisDependency, cls).__new__(cls)
                    cls._instance._initialize_pool()
        return cls._instance

    def _initialize_pool(self):
        self._conn_pool = ConnectionPool(
            host=settings.redis_settings.host,
            port=settings.redis_settings.port,
            db=settings.redis_settings.db_number,
            password=settings.redis_settings.password.get_secret_value(),
        )

    @property
    def redis_client_factory(self) -> Callable[[], Redis]:
        return partial(Redis, connection_pool=self._conn_pool)
