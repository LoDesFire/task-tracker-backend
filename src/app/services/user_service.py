from pydantic import SecretStr

from src.app.repositories import UserRepository
from src.app.repositories.kafka_repository import KafkaRepository
from src.app.repositories.redis_repository import RedisRepository
from src.app.repositories.ses_repository import SESRepository
from src.app.services.jwt_service import JWTService
from src.constants import KafkaUserEventTypes
from src.helpers.codes_helper import generate_verification_code
from src.helpers.cryptography_helper import hash_password, verify_password
from src.helpers.exceptions.repository_exceptions import (
    RedisRepositoryException,
    RepositoryIntegrityException,
    RepositoryNotFoundException,
)
from src.helpers.exceptions.service_exceptions import JWTServiceException
from src.helpers.exceptions.service_exceptions.user_exceptions import (
    UserNotFoundException,
    UserServiceException,
)
from src.helpers.jwt_helper import JWTTokenPayload
from src.schemas.kafka_schemas import UserInfoSchema
from src.schemas.user_schemas import (
    UpdateEmailUserSchema,
    UpdatePasswordUserSchema,
    UpdateUserSchema,
)


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        jwt_service: JWTService,
        ses_repository: SESRepository,
        redis_repository: RedisRepository,
        kafka_repository: KafkaRepository,
    ):
        self.user_repo = user_repository
        self.jwt_service = jwt_service
        self.ses_repo = ses_repository
        self.redis_repo = redis_repository
        self.kafka_repo = kafka_repository

    async def update_user(
        self,
        auth_context: JWTTokenPayload,
        user_schema: UpdateUserSchema,
    ):
        try:
            updated_user = await self.user_repo.update(
                auth_context.sub,
                **user_schema.model_dump(),
            )
        except RepositoryNotFoundException as exc:
            raise UserNotFoundException("Invalid access token") from exc

        await self.kafka_repo.produce_user_event(
            KafkaUserEventTypes.UPDATE,
            UserInfoSchema(
                id=str(updated_user.id),
                email=updated_user.email,
                username=updated_user.username,
            ),
        )

        return updated_user

    async def get_user(self, auth_context: JWTTokenPayload):
        try:
            return await self.user_repo.get_by_id(auth_context.sub)
        except RepositoryNotFoundException as exc:
            raise UserNotFoundException("Invalid access token") from exc

    async def delete_user(self, password: SecretStr, auth_context: JWTTokenPayload):
        try:
            user = await self.user_repo.get_by_id(auth_context.sub)
        except RepositoryNotFoundException as exc:
            raise UserNotFoundException("Invalid access token") from exc
        if not verify_password(password.get_secret_value(), user.hashed_password):
            raise UserServiceException("Invalid password")

        try:
            await self.jwt_service.revoke_all_tokens(
                subject=auth_context.sub,
            )
            await self.user_repo.update(auth_context.sub, **dict(is_active=False))
        except (RepositoryNotFoundException, JWTServiceException) as exc:
            raise UserNotFoundException("Invalid access token") from exc

    async def update_password(
        self,
        auth_context: JWTTokenPayload,
        password_schema: UpdatePasswordUserSchema,
    ):
        try:
            user = await self.user_repo.get_by_id(auth_context.sub)
        except RepositoryNotFoundException as exc:
            raise UserNotFoundException("Invalid access token") from exc

        if not verify_password(
            password_schema.old_password.get_secret_value(), user.hashed_password
        ):
            raise UserServiceException("Invalid old password")

        await self.user_repo.update(
            auth_context.sub,
            **dict(
                hashed_password=hash_password(
                    password_schema.new_password.get_secret_value()
                )
            ),
        )
        try:
            await self.jwt_service.revoke_all_tokens(
                subject=auth_context.sub,
            )
        except JWTServiceException as exc:
            raise UserNotFoundException("Invalid access token") from exc

    async def update_email(
        self,
        email_schema: UpdateEmailUserSchema,
        auth_context: JWTTokenPayload,
    ):
        try:
            user = await self.user_repo.get_by_id(auth_context.sub)
        except RepositoryNotFoundException as exc:
            raise UserNotFoundException("Invalid access token") from exc

        if user.email == email_schema.email:
            raise UserServiceException("This email is already in use")

        verification_code = generate_verification_code()
        try:
            updated_user = await self.user_repo.update(
                auth_context.sub,
                **dict(email=str(email_schema.email), is_verified=False),
            )
            await self.jwt_service.revoke_all_tokens(
                subject=auth_context.sub,
            )
        except JWTServiceException as exc:
            raise UserNotFoundException("Invalid access token") from exc
        except RepositoryIntegrityException as exc:
            raise UserServiceException("User with this email already exists") from exc

        try:
            await self.redis_repo.create_verification_code_record(
                verification_code, auth_context.sub, is_force=True
            )
            await self.ses_repo.send_verification_code_email(
                str(email_schema.email), verification_code
            )
        except RedisRepositoryException as exc:
            raise UserServiceException("Internal error") from exc

        return updated_user
