from typing import Any

from pydantic import BaseModel, SecretStr, field_validator
from pydantic_core.core_schema import ValidationInfo

from src.helpers.codes_helper import validate_password


class PasswordValidatorMixin:
    """
    Mixin for password validation with configurable rules.
    Add '__validate_password_fields__' to your model with field names to validate.
    """

    __validate_password_fields__: tuple[str]

    @field_validator("*", mode="after")
    @classmethod
    def validate_password(cls, field_value: Any, info: ValidationInfo) -> Any:
        if info.field_name not in cls.__validate_password_fields__:
            return field_value

        if not isinstance(field_value, SecretStr):
            raise TypeError(f"Field '{info.field_name}' must be SecretStr")

        errors = validate_password(field_value.get_secret_value())

        if errors:
            raise ValueError("\n".join(errors))

        return field_value


class ValidatedPasswordMixin(BaseModel, PasswordValidatorMixin):
    __validate_password_fields__ = ("password",)
    password: SecretStr


class PasswordMixin(BaseModel):
    password: SecretStr
