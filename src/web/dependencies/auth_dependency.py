from fastapi import HTTPException
from fastapi.params import Depends, Header
from starlette import status

from src.app.repositories.redis_repository import RedisRepository
from src.app.services.jwt_service import JWTService
from src.constants import JWTTokenType
from src.helpers.exceptions.service_exceptions import JWTServiceException
from src.helpers.jwt_helper import JWTTokenPayload
from src.web.dependencies.redis_dependency import RedisDependency


def get_redis_repository(redis: RedisDependency = Depends(RedisDependency)):
    return RedisRepository(redis.redis_client_factory)


def get_jwt_service(redis_repository: RedisRepository = Depends(get_redis_repository)):
    return JWTService(redis_repo=redis_repository)


def auth_dependency(is_verified=True, is_admin=False):
    """
    Authorizing user via JWT token
    :param is_verified: if checked then endpoint will be available only for
    verified users
    :param is_admin: if checked then endpoint will be available only for admins
    :raises HTTPException: if user not authenticated or not authorized
    :return JWTTokenPayload
    """

    async def wrapped(
        jwt_service: JWTService = Depends(get_jwt_service),
        authorization: str = Header(),
    ) -> JWTTokenPayload:
        if not authorization.startswith("Bearer"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
            )
        access_token = authorization.split()[1]
        try:
            decoded_token = await jwt_service.decode_token(
                access_token,
                JWTTokenType.ACCESS,
            )
            if is_verified and not decoded_token.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your account is not verified. "
                    "Please check your email or request a verification code.",
                )
            if is_admin and not decoded_token.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token",
                )

        except JWTServiceException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
            )
        return decoded_token

    return wrapped
