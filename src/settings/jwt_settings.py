from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    private_key: SecretStr
    public_key: str
    access_token_ttl_minutes: int
    refresh_token_ttl_minutes: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="JWT_",
    )
