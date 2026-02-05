from pydantic_settings import BaseSettings, SettingsConfigDict


class PasswordSettings(BaseSettings):
    is_uppercase: bool = True
    is_lowercase: bool = True
    is_digits: bool = True
    is_special_characters: bool = True
    min_length: int = 12
    special_characters: str = "?!_=+}{@-#$%~*&]["

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="PASSWORD_",
    )
