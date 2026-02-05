from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AWSSettings(BaseSettings):
    endpoint_url: str
    region_name: str
    access_key_id: SecretStr
    secret_access_key: SecretStr

    s3_service_bucket_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="AWS_",
    )
