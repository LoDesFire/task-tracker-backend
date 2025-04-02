from fastapi import Depends

from src.app.repositories import UserRepository
from src.app.services.auth_service import AuthService
from src.web.dependencies.db_dependency import DBDependency


def get_user_repository(db: DBDependency = Depends(DBDependency)):
    return UserRepository(db.db_session)


def get_user_service(user_repository: UserRepository = Depends(get_user_repository)):
    return AuthService(user_repository)
