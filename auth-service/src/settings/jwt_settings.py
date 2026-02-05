from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    private_key: SecretStr = "private-key"
    public_key: str = "public-key"
    access_token_ttl_minutes: int = 5
    refresh_token_ttl_minutes: int = 86400

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="JWT_",
    )
