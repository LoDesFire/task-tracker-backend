from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    secret: SecretStr
    access_token_expiration_minutes: int
    refresh_token_expiration_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", env_prefix="JWT_"
    )
