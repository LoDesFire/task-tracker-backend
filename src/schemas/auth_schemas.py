import datetime

from pydantic import BaseModel, EmailStr


class EmailMixin(BaseModel):
    email: EmailStr


class PasswordMixin(BaseModel):
    password: str


class UsernameMixin(BaseModel):
    username: str


class RegisterInputSchema(PasswordMixin, EmailMixin, UsernameMixin):
    pass


class RegistrationOutputSchema(EmailMixin, UsernameMixin):
    created_at: datetime.datetime


class LoginSchema(PasswordMixin, EmailMixin):
    pass


class JWTPayloadUserSchema(BaseModel):
    is_admin: bool = False


class TokensSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
