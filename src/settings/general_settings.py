from pydantic import SecretStr
from pydantic_settings import BaseSettings

from src.settings.db_settings import DBSettings
from src.settings.jwt_settings import JWTSettings


class Settings(BaseSettings):
    db_settings: DBSettings = DBSettings()
    jwt_settings: JWTSettings = JWTSettings()


settings = Settings()
