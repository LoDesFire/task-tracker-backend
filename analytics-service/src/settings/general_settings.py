from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.kafka_settings import KafkaSettings
from settings.mongo_settings import MongoSettings


class Settings(BaseSettings):
    kafka_settings: KafkaSettings = KafkaSettings()
    mongo_settings: MongoSettings = MongoSettings()
    jwt_public_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
