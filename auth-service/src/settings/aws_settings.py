from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSSettings(BaseSettings):
    endpoint_url: str = "localhost"
    region_name: str = "region-name"
    access_key_id: SecretStr = "access-key-id"
    secret_access_key: SecretStr = "secret-access-key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="AWS_",
    )
