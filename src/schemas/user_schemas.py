from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, SecretStr, model_validator
from typing_extensions import Self

from src.schemas.password_mixin import PasswordMixin, PasswordValidatorMixin


class UpdateEmailUserSchema(BaseModel):
    email: EmailStr


class UpdatePasswordUserSchema(BaseModel, PasswordValidatorMixin):
    __validate_password_fields__ = ("new_password",)

    old_password: SecretStr
    new_password: SecretStr

    @model_validator(mode="after")
    def check_passwords_inequality(self) -> Self:
        if self.new_password.get_secret_value() == self.old_password.get_secret_value():
            raise ValueError("Passwords must be different")
        return self


class UpdateUserSchema(BaseModel):
    username: Optional[str] = Field(None)

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        for field_name, field_val in self.model_dump().items():
            if field_val is not None:
                return self

        raise ValueError("Must have at least one field")


class UserOutputSchema(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    created_at: datetime


class PasswordSchema(PasswordMixin):
    """password schema"""
