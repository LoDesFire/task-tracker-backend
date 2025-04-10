import datetime
from typing import Callable

from redis.asyncio import Redis
from redis.exceptions import RedisError

from src.constants import RevokeTokensScope
from src.helpers.exceptions.repository_exceptions import (
    RedisRepositoryAlreadyExistsException,
    RedisRepositoryException,
)
from src.settings.general_settings import settings


class RedisRepository:
    def __init__(self, redis_factory: Callable[[], Redis]):
        self.__redis_factory = redis_factory

    @staticmethod
    def app_tokens_hash(app_id: str):
        """
        :param app_id: app_id in the jwt token
        :return:
        prefix for the app tokens hash object in the Redis
        """
        return f"{settings.redis_settings.app_tokens_hash_prefix}:{app_id}"

    @staticmethod
    def user_apps_hash(subject):
        """
        :param subject: sub in the jwt token
        :return:
        Prefix for the user apps hash object in the Redis
        """
        return f"{settings.redis_settings.user_apps_hash_prefix}:{subject}"

    @staticmethod
    def verif_code_name(subject: str):
        """
        :param subject: sub in the jwt token
        :return:
        Prefix for the verification code object in the Redis
        """
        return f"{settings.redis_settings.verification_codes_hash_prefix}:{subject}"

    async def create_token_record(
        self,
        subject: str,
        app_id: str,
        jwt_id: str,
        exp_at_timestamp: int,
    ):
        """
        Temporarily saves jwt_id into the Redis for the jwt verification process
        :param subject: sub in the jwt token
        :param app_id: app_id in the jwt token
        :param jwt_id: jwt_id in jwt token
        :param exp_at_timestamp: exp in the jwt token
        :raises RedisRepositoryException:
        """
        apps_hash_name = self.user_apps_hash(subject)
        tokens_hash_name = self.app_tokens_hash(app_id)
        try:
            await self.__update_token_record(
                apps_hash_name,
                tokens_hash_name,
                exp_at_timestamp,
                app_id,
                jwt_id,
            )
        except RedisError as exc:
            raise RedisRepositoryException("Unable to create the token record") from exc

    async def __update_token_record(
        self,
        apps_hash_name: str,
        tokens_hash_name: str,
        exp_at_timestamp: int,
        app_id: str,
        jwt_id: str,
    ):
        async with self.__redis_factory() as redis:
            pipeline = await redis.pipeline()
            # Updating apps hash
            await pipeline.hsetnx(apps_hash_name, app_id, "1")
            await pipeline.hexpireat(
                apps_hash_name,
                exp_at_timestamp,
                app_id,
                gt=True,
            )

            # Updating tokens hash
            await pipeline.hset(tokens_hash_name, jwt_id, "1")
            await pipeline.hexpireat(tokens_hash_name, exp_at_timestamp, jwt_id)
            await pipeline.expireat(
                tokens_hash_name,
                exp_at_timestamp,
                gt=exp_at_timestamp,
            )
            await pipeline.execute()

    async def is_token_active(self, app_id: str, jwt_id: str):
        tokens_hash_name = self.app_tokens_hash(app_id)
        try:
            async with self.__redis_factory() as redis:
                token_value = await redis.hget(tokens_hash_name, jwt_id)
                if not token_value:
                    return False

                return True
        except RedisError as exc:
            raise RedisRepositoryException("Unable to obtain token activity") from exc

    async def revoke_tokens(
        self,
        subject: str,
        app_id: str,
        jwt_id: str,
        scope: RevokeTokensScope,
    ):
        """
        Removes suitable tokens from the Redis according to the given scope
        :param subject: sub in the jwt token
        :param app_id: app_id in the jwt token
        :param jwt_id: jwt_id in jwt token
        :param scope: revoke scope
        :raises RedisRepositoryException:
        """
        apps_hash_name = self.user_apps_hash(subject)
        tokens_hash_name = self.app_tokens_hash(app_id)
        try:
            await self.__delete_token_records(
                scope,
                apps_hash_name,
                app_id,
                tokens_hash_name,
                jwt_id,
            )
        except RedisError as exc:
            raise RedisRepositoryException("Failed to revoke the tokens") from exc

    async def __delete_token_records(
        self,
        scope: RevokeTokensScope,
        apps_hash_name: str,
        app_id: str,
        tokens_hash_name: str,
        jwt_id: str,
    ):
        async with self.__redis_factory() as redis:
            match scope:
                case RevokeTokensScope.CURRENT_APP:
                    await redis.hdel(apps_hash_name, app_id)
                    await redis.delete(tokens_hash_name)
                case RevokeTokensScope.ALL:
                    async for iter_app_id, val in redis.hscan_iter(apps_hash_name):
                        await redis.delete(self.app_tokens_hash(iter_app_id.decode()))
                    await redis.delete(apps_hash_name)
                case RevokeTokensScope.THE_TOKEN:
                    await redis.hdel(tokens_hash_name, jwt_id)

    async def create_verification_code_record(
        self,
        verification_code: str,
        subject: str,
        is_force: bool = False,
    ):
        """
        Created a new object in the Redis for the verification process
        :param is_force: if checked then set verification code even if already exists
        :param verification_code: verification_code
        :param subject: sub in the jwt token
        :raises RedisRepositoryException:
        :raises RedisRepositoryAlreadyExists: if force parameter unchecked
        """
        verif_code_name = self.verif_code_name(subject)
        ttl = int(
            datetime.timedelta(
                minutes=settings.verification_code_ttl_minutes
            ).total_seconds()
        )
        try:
            async with self.__redis_factory() as redis:
                response = await redis.set(
                    verif_code_name,
                    verification_code,
                    ex=ttl,
                    nx=not is_force,
                )
                if not is_force and response is None:
                    raise RedisRepositoryAlreadyExistsException("Code already exists")
        except RedisError as exc:
            raise RedisRepositoryException("Failed to create the object") from exc

    async def check_verification_code(
        self,
        verification_code: str,
        subject: str,
    ) -> bool:
        """
        Checks verification code with the given verification_code
        :param verification_code: verification_code
        :param subject: sub in the jwt token
        :raises RedisRepositoryException:
        """
        verif_code_name = self.verif_code_name(subject)

        try:
            async with self.__redis_factory() as redis:
                code = await redis.get(verif_code_name)
                if code is not None and code.decode("utf-8") == verification_code:
                    await redis.delete(verif_code_name)
                    return True
        except RedisError as exc:
            raise RedisRepositoryException("Check failed") from exc

        return False
