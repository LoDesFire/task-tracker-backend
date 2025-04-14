from pydantic_settings import BaseSettings, SettingsConfigDict

from src.settings.aws_settings import AWSSettings
from src.settings.db_settings import DBSettings
from src.settings.jwt_settings import JWTSettings
from src.settings.password_settings import PasswordSettings
from src.settings.redis_settings import RedisSettings


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()
    jwt_settings: JWTSettings = JWTSettings()
    redis_settings: RedisSettings = RedisSettings()
    aws_settings: AWSSettings = AWSSettings()
    password_settings: PasswordSettings = PasswordSettings()

    ses_source_email: str
    verification_code_ttl_minutes: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
