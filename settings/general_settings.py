from pydantic_settings import BaseSettings

from settings.db_settings import DBSettings


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()


settings = Settings()
