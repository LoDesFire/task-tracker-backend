from src.schemas import EmailMixin, UsernameMixin


class RegisterUserAppSchema(UsernameMixin, EmailMixin):
    hashed_password: str
    is_active: bool = True
