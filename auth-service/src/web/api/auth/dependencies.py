from fastapi import Depends

from src.app.repositories import UserRepository
from src.app.repositories.kafka_repository import KafkaRepository
from src.app.repositories.redis_repository import RedisRepository
from src.app.repositories.ses_repository import SESRepository
from src.app.services.auth_service import AuthService
from src.app.services.jwt_service import JWTService
from src.web.dependencies.auth_dependency import get_jwt_service, get_redis_repository
from src.web.dependencies.repository_dependencies import (
    get_kafka_repository,
    get_ses_repository,
    get_user_repository,
)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service),
    redis_repository: RedisRepository = Depends(get_redis_repository),
    ses_repository: SESRepository = Depends(get_ses_repository),
    kafka_repository: KafkaRepository = Depends(get_kafka_repository),
):
    return AuthService(
        user_repo=user_repository,
        jwt_service=jwt_service,
        redis_repo=redis_repository,
        ses_repo=ses_repository,
        kafka_repository=kafka_repository,
    )
