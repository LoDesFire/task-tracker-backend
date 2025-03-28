from fastapi import Depends

from app.database.db_dependency import DBDependency
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def get_user_repository(db: DBDependency = Depends(DBDependency)):
    return UserRepository(db.db_session)


def get_user_service(user_repository: UserRepository = Depends(get_user_repository)):
    return AuthService(user_repository)
