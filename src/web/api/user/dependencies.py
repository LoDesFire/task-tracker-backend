from fastapi import Depends

from src.app.repositories import UserRepository
from src.app.repositories.redis_repository import RedisRepository
from src.app.repositories.ses_repository import SESRepository
from src.app.services.jwt_service import JWTService
from src.app.services.user_service import UserService
from src.web.dependencies.auth_dependency import get_jwt_service
from src.web.dependencies.db_dependency import DBDependency
from src.web.dependencies.redis_dependency import RedisDependency
from src.web.dependencies.ses_dependency import SESDependency


def get_user_repository(db: DBDependency = Depends(DBDependency)):
    return UserRepository(db.db_session)


def get_ses_repository(ses_dep: SESDependency = Depends(SESDependency)):
    return SESRepository(ses_dep.ses_client_factory)


def get_redis_repository(redis_dep: RedisDependency = Depends(RedisDependency)):
    return RedisRepository(redis_dep.redis_client_factory)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service),
    ses_repository: SESRepository = Depends(get_ses_repository),
    redis_repo: RedisRepository = Depends(get_redis_repository),
) -> UserService:
    return UserService(
        user_repository=user_repository,
        jwt_service=jwt_service,
        ses_repository=ses_repository,
        redis_repository=redis_repo,
    )
