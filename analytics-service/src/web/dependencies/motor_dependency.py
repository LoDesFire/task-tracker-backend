from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from settings import settings


class MotorDependency:
    __client: Optional[AsyncIOMotorClient] = None

    @classmethod
    def init_connection(cls):
        cls.__client = AsyncIOMotorClient(
            settings.mongo_settings.connection_string,
        )

    @classmethod
    def close_connections(cls):
        if cls.__client is not None:
            cls.__client.close()
            cls.__client = None

    @property
    def client(self):
        if self.__client is None:
            self.init_connection()
        return self.__client
