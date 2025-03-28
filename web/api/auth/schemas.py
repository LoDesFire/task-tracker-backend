from pydantic import BaseModel, EmailStr


class UserEmailSchema(BaseModel):
    email: EmailStr


class LoginUserSchema(UserEmailSchema):
    password: str


class RegisterUserSchema(LoginUserSchema):
    username: str


class VerificationConfirmationSchema(BaseModel):
    confirmation_code: str
