from fastapi import Depends

from src.app.repositories import UserRepository
from src.app.repositories.kafka_repository import KafkaRepository
from src.app.repositories.redis_repository import RedisRepository
from src.app.repositories.ses_repository import SESRepository
from src.web.dependencies.db_dependency import DBDependency
from src.web.dependencies.kafka_producer_dependency import KafkaProducerDependency
from src.web.dependencies.redis_dependency import RedisDependency
from src.web.dependencies.ses_dependency import SESDependency


def get_user_repository(db: DBDependency = Depends(DBDependency)):
    return UserRepository(db.db_session)


def get_ses_repository(ses_dep: SESDependency = Depends(SESDependency)):
    return SESRepository(ses_dep.ses_client_factory)


def get_redis_repository(redis_dep: RedisDependency = Depends(RedisDependency)):
    return RedisRepository(redis_dep.redis_client_factory)


def get_kafka_repository(
    kafka_dependency: KafkaProducerDependency = Depends(KafkaProducerDependency),
):
    return KafkaRepository(kafka_producer_factory=kafka_dependency.get_producer)
