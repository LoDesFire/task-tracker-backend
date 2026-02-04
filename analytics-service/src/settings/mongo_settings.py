from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str

    db_name: str

    @property
    def connection_string(self):
        return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="MONGO_",
    )