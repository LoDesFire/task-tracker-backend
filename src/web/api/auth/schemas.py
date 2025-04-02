from pydantic import BaseModel

from src.schemas.auth_schemas import EmailMixin


class UserEmailSchema(EmailMixin):
    pass


class VerificationConfirmationSchema(BaseModel):
    confirmation_code: str
