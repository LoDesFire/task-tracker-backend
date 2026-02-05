from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    password: SecretStr = "password"
    host: str = "localhost"
    port: int = 6379
    db_number: int = 0

    app_tokens_hash_prefix: str = "app_tks"
    user_apps_hash_prefix: str = "usr_apps"
    verification_codes_hash_prefix: str = "verification_codes"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="REDIS_",
    )
