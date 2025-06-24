from fastapi import Depends

from src.app.repositories import UserRepository
from src.app.repositories.kafka_repository import KafkaRepository
from src.app.repositories.redis_repository import RedisRepository
from src.app.repositories.ses_repository import SESRepository
from src.app.services.jwt_service import JWTService
from src.app.services.user_service import UserService
from src.web.dependencies.auth_dependency import get_jwt_service
from src.web.dependencies.repository_dependencies import (
    get_kafka_repository,
    get_redis_repository,
    get_ses_repository,
    get_user_repository,
)


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service),
    ses_repository: SESRepository = Depends(get_ses_repository),
    redis_repo: RedisRepository = Depends(get_redis_repository),
    kafka_repository: KafkaRepository = Depends(get_kafka_repository),
) -> UserService:
    return UserService(
        user_repository=user_repository,
        jwt_service=jwt_service,
        ses_repository=ses_repository,
        redis_repository=redis_repo,
        kafka_repository=kafka_repository,
    )
