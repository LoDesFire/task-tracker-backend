from src.app.repositories.exceptions import (
    RepositoryIntegrityError,
    RepositoryNotFoundException,
)
from src.app.repositories.user_repository import UserRepository
from src.app.schemas import RegisterUserAppSchema
from src.helpers.cryptography_helper import hash_password, verify_password
from src.helpers.exceptions.service_exceptions import (
    LoginException,
    RegistrationException,
)
from src.helpers.jwt_helper import create_access_token, create_refresh_token
from src.schemas import RegisterInputSchema
from src.schemas.auth_schemas import (
    JWTPayloadUserSchema,
    LoginSchema,
    RegistrationOutputSchema,
    TokensSchema,
)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, register_schema: RegisterInputSchema):
        register_app_schema = RegisterUserAppSchema(
            **register_schema.model_dump(),
            hashed_password=hash_password(register_schema.password),
        )

        try:
            user = await self.user_repo.create_user(register_app_schema)
            # TODO: Send verification email

        except RepositoryIntegrityError as e:
            raise RegistrationException("Email is already in use") from e

        return user.to_pydantic(RegistrationOutputSchema)

    async def login_user(self, login_schema: LoginSchema):
        try:
            user = await self.user_repo.get_user_by_email(email=str(login_schema.email))
        except RepositoryNotFoundException as e:
            raise LoginException("Invalid email or password") from e

        if not verify_password(login_schema.password, user.hashed_password):
            raise LoginException("Invalid email or password")

        if not user.is_active:
            raise LoginException("Your account is blocked")

        if not user.is_verified:
            raise LoginException(
                "Your account is not verified. "
                "Please check your email or request a verification code."
            )

        access_token = create_access_token(
            subject=user.email, jwt_payload=JWTPayloadUserSchema(is_admin=user.is_admin)
        )
        refresh_token = create_refresh_token(subject=user.email)

        # TODO: Save access_token and refresh_tokens in Redis with exp time
        return TokensSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
