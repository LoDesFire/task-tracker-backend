from src.app.repositories.redis_repository import RedisRepository
from src.constants import JWTTokenType
from src.helpers.exceptions.helpers_exceptions import JWTDecodeException
from src.helpers.exceptions.repository_exceptions import RedisRepositoryException
from src.helpers.exceptions.service_exceptions import JWTServiceException
from src.helpers.jwt_helper import (
    JWTToken,
    JWTTokenPayload,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.schemas.auth_schemas import JWTPayloadUserSchema


class JWTService:
    def __init__(self, redis_repo: RedisRepository):
        self.redis_repo = redis_repo

    async def __issue_access_token(
        self,
        subject: str,
        payload: JWTPayloadUserSchema,
    ) -> JWTToken:
        """
        Creates an access token and saves jwt_id in the Redis
        :param subject: user's id
        :param payload: payload for jwt token
        :return:
        jwt token object with payload and token string
        """
        jwt_token = create_access_token(subject, payload)
        try:
            await self.redis_repo.create_token_record(
                subject,
                jwt_token.payload.app_id,
                jwt_token.payload.jwt_id,
                jwt_token.payload.exp,
            )
        except RedisRepositoryException as exc:
            raise JWTServiceException(internal_message=exc.message) from exc

        return jwt_token

    async def __issue_refresh_token(
        self,
        subject: str,
        app_id: str | None = None,
    ) -> JWTToken:
        """
        Creates a refresh token and saves jwt_id in the Redis
        :param subject: user's id
        :param app_id: app_id from the parental jwt token
        :return:
        jwt token object with payload and token string
        """
        jwt_token = create_refresh_token(subject, app_id)
        try:
            await self.redis_repo.create_token_record(
                subject,
                jwt_token.payload.app_id,
                jwt_token.payload.jwt_id,
                jwt_token.payload.exp,
            )
        except RedisRepositoryException as exc:
            raise JWTServiceException(internal_message=exc.message) from exc

        return jwt_token

    async def issue_token_pair(self, subject: str, payload: JWTPayloadUserSchema):
        """
        Creates the couple of access and refresh tokens with a similar app_id
        :param subject: user's id
        :param payload: payload for jwt token
        :return: tokens couple
        :raises JWTServiceException
        """
        access_token = await self.__issue_access_token(subject, payload)

        refresh_token = await self.__issue_refresh_token(
            subject=subject,
            app_id=(
                access_token.payload.app_id
                if payload.app_id is None
                else payload.app_id
            ),
        )
        return {
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
            "token_type": "bearer",
        }

    async def decode_token(self, token: str, token_type: JWTTokenType):
        """
        Decodes a token
        :param token: the token to decode
        :param token_type: token type
        :return: the token's payload
        :raises JWTServiceException
        """
        try:
            jwt_payload = decode_token(token, token_type)

            if not (
                await self.redis_repo.is_token_active(
                    jwt_payload.app_id,
                    jwt_payload.jwt_id,
                )
            ):
                raise JWTServiceException(internal_message="Token is inactive")
        except RedisRepositoryException as exc:
            raise JWTServiceException(internal_message=exc.message) from exc
        except JWTDecodeException as exc:
            raise JWTServiceException(
                internal_message="Failed to decode the JWT token"
            ) from exc

        return jwt_payload

    async def renew_tokens(
        self,
        old_refresh_token: str,
        old_decoded_token: JWTTokenPayload,
        new_payload: JWTPayloadUserSchema,
    ):
        """
        Returns new access token and old refresh token
        :param old_refresh_token:
        :param old_decoded_token:
        :param new_payload:
        :return:
        dictionary with renewed token
        """
        new_payload = new_payload.model_copy(
            update={"app_id": old_decoded_token.app_id}
        )
        new_access_token = await self.__issue_access_token(
            old_decoded_token.sub,
            new_payload,
        )

        return {
            "access_token": new_access_token.token,
            "refresh_token": old_refresh_token,
            "token_type": "bearer",
        }

    async def revoke_all_tokens(self, subject: str):
        try:
            await self.redis_repo.revoke_all_tokens(
                subject=subject,
            )
        except RedisRepositoryException as exc:
            raise JWTServiceException(internal_message=exc.message) from exc

    async def revoke_current_app_tokens(self, subject: str, app_id: str):
        try:
            await self.redis_repo.revoke_current_app_tokens(
                subject=subject,
                app_id=app_id,
            )
        except RedisRepositoryException as exc:
            raise JWTServiceException(internal_message=exc.message) from exc

    async def revoke_current_token(self, app_id: str, jwt_id: str):
        try:
            await self.redis_repo.revoke_current_token(
                app_id=app_id,
                jwt_id=jwt_id,
            )
        except RedisRepositoryException as exc:
            raise JWTServiceException(internal_message=exc.message) from exc
