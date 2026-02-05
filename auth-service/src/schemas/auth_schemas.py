import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from src.schemas.password_mixin import PasswordMixin, ValidatedPasswordMixin


class EmailMixin(BaseModel):
    email: EmailStr


class UsernameMixin(BaseModel):
    username: str


class UserEmailSchema(EmailMixin):
    """UserEmailSchema"""


class RegisterInputSchema(ValidatedPasswordMixin, EmailMixin, UsernameMixin):
    """RegisterInputSchema"""


class RegistrationOutputSchema(EmailMixin, UsernameMixin):
    created_at: datetime.datetime


class LoginSchema(PasswordMixin, EmailMixin):
    """LoginSchema"""


class JWTPayloadUserSchema(BaseModel):
    is_admin: bool = False
    is_verified: bool = True
    app_id: Optional[str] = None


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class VerificationConfirmationSchema(BaseModel):
    confirmation_code: str
