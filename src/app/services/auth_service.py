import random
from contextlib import suppress

from src.app.repositories.redis_repository import RedisRepository
from src.app.repositories.ses_repository import SESRepository
from src.app.repositories.user_repository import UserRepository
from src.app.schemas import RegisterUserAppSchema
from src.app.services.jwt_service import JWTService
from src.constants import JWTTokenType, RevokeTokensScope
from src.helpers.codes_helper import generate_password, generate_verification_code
from src.helpers.cryptography_helper import hash_password, verify_password
from src.helpers.exceptions.repository_exceptions import (
    RedisRepositoryAlreadyExistsException,
    RedisRepositoryException,
    RepositoryIntegrityError,
    RepositoryNotFoundException,
)
from src.helpers.exceptions.service_exceptions import (
    JWTServiceException,
    LoginException,
    RefreshingException,
    RegistrationException,
    RevokeException,
)
from src.helpers.exceptions.service_exceptions.auth_exceptions import (
    VerificationException,
)
from src.helpers.jwt_helper import JWTTokenPayload
from src.schemas import RegisterInputSchema
from src.schemas.auth_schemas import (
    JWTPayloadUserSchema,
    LoginSchema,
    RefreshTokenSchema,
    RegistrationOutputSchema,
)


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        jwt_service: JWTService,
        redis_repo: RedisRepository,
        ses_repo: SESRepository,
    ):
        self.user_repo = user_repo
        self.jwt_service = jwt_service
        self.redis_repo = redis_repo
        self.ses_repo = ses_repo

    async def register_user(self, register_schema: RegisterInputSchema):
        register_app_schema = RegisterUserAppSchema(
            **register_schema.model_dump(),
            hashed_password=hash_password(register_schema.password),
        )

        verification_code = generate_verification_code()
        try:
            user = await self.user_repo.create_user(register_app_schema)

            await self.ses_repo.send_verification_code_email(
                user.email,
                verification_code,
            )

        except RepositoryIntegrityError as exc:
            raise RegistrationException("Email is already in use") from exc

        with suppress(RedisRepositoryException):
            await self.redis_repo.create_verification_code_record(
                verification_code,
                str(user.id),
                is_force=True,
            )

        return user.to_pydantic(RegistrationOutputSchema)

    async def login_user(self, login_schema: LoginSchema):
        try:
            user = await self.user_repo.get_user_by_email(email=str(login_schema.email))
        except RepositoryNotFoundException as exc:
            raise LoginException("Invalid email or password") from exc

        if not verify_password(login_schema.password, user.hashed_password):
            raise LoginException("Invalid email or password")

        if not user.is_active:
            raise LoginException("Your account is blocked")

        return await self.jwt_service.issue_token_pair(
            str(user.id),
            JWTPayloadUserSchema(is_admin=user.is_admin, is_verified=user.is_verified),
        )

    async def refresh_user_tokens(self, refresh_token_schema: RefreshTokenSchema):
        try:
            decoded_token = await self.jwt_service.decode_token(
                refresh_token_schema.refresh_token,
                JWTTokenType.REFRESH,
            )
        except JWTServiceException as exc:
            raise RefreshingException("Invalid refresh token") from exc

        try:
            user = await self.user_repo.get_user_by_id(user_id=decoded_token.sub)
        except RepositoryNotFoundException as exc:
            raise RefreshingException("Invalid refresh token") from exc

        if not user.is_active:
            raise RefreshingException("Your account is blocked")

        if not user.is_verified:
            raise RefreshingException(
                "Your account is not verified. "
                "Please check your email or request a verification code."
            )

        payload = JWTPayloadUserSchema(
            is_admin=user.is_admin,
            is_verified=user.is_verified,
        )

        return await self.jwt_service.renew_tokens(
            old_refresh_token=refresh_token_schema.refresh_token,
            old_decoded_token=decoded_token,
            new_payload=payload,
        )

    async def revoke_user_tokens(
        self, access_token_payload: JWTTokenPayload, scope: RevokeTokensScope
    ):
        try:
            await self.jwt_service.revoke_tokens(access_token_payload, scope)
        except JWTServiceException as exc:
            raise RevokeException("Invalid access token") from exc

    async def reset_password(self, access_token_payload: JWTTokenPayload):
        try:
            user = await self.user_repo.get_user_by_id(access_token_payload.sub)
        except RepositoryNotFoundException as exc:
            raise RefreshingException("Invalid access token") from exc

        new_password = generate_password(
            length=random.randint(12, 16),
            digit_percent=random.randint(20, 30),
            special_percent=random.randint(10, 20),
        )

        await self.ses_repo.send_password_reset_email(
            email=str(user.email),
            password=new_password,
        )

        await self.jwt_service.revoke_tokens(
            access_token_payload,
            RevokeTokensScope.ALL,
        )

        await self.user_repo.update_user_by_email(
            user_email=str(user.email),
            user_update_data=dict(hashed_password=hash_password(new_password)),
        )

    async def send_verification_code(self, access_token_payload: JWTTokenPayload):
        if access_token_payload.is_verified:
            raise VerificationException("User is already verified")

        try:
            user = await self.user_repo.get_user_by_id(access_token_payload.sub)
        except RepositoryNotFoundException as exc:
            raise VerificationException("Invalid access token") from exc

        code = generate_verification_code()

        try:
            await self.redis_repo.create_verification_code_record(
                code,
                access_token_payload.sub,
            )
        except RedisRepositoryAlreadyExistsException as exc:
            raise VerificationException("Verification code already exists") from exc
        except RedisRepositoryException as exc:
            raise VerificationException("Temporarily unavailable") from exc

        await self.ses_repo.send_verification_code_email(
            email=str(user.email),
            verification_code=code,
        )

    async def confirm_verification_code(
        self,
        code: str,
        access_token_payload: JWTTokenPayload,
    ):
        if access_token_payload.is_verified:
            raise VerificationException("User is already verified")

        if not await self.redis_repo.check_verification_code(
            code,
            access_token_payload.sub,
        ):
            raise VerificationException("Invalid verification code")

        try:
            user = await self.user_repo.get_user_by_id(access_token_payload.sub)
            await self.user_repo.update_user_by_email(
                user_email=user.email,
                user_update_data=dict(is_verified=True),
            )
            await self.jwt_service.revoke_tokens(
                access_token_payload,
                RevokeTokensScope.THE_TOKEN,
            )
        except RepositoryNotFoundException as exc:
            raise VerificationException("Invalid user") from exc
        except RepositoryIntegrityError as exc:
            raise VerificationException("Internal error") from exc
        except JWTServiceException:
            pass
