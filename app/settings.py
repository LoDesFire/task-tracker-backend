from pydantic_settings import BaseSettings

from app.database.settings import DBSettings


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()


settings = Settings()
