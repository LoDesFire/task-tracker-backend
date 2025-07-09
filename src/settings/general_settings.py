from pydantic_settings import BaseSettings, SettingsConfigDict

from settings.s3_settings import AWSSettings
from src.settings.db_settings import DBSettings


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()
    aws_settings: AWSSettings = AWSSettings()


    jwt_public_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
