from fastapi import Depends

from src.app.repositories import UserRepository
from src.app.services.admin_service import AdminService
from src.app.services.jwt_service import JWTService
from src.web.dependencies.auth_dependency import get_jwt_service
from src.web.dependencies.repository_dependencies import (
    get_user_repository,
)


async def get_admin_service(
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_service: JWTService = Depends(get_jwt_service),
):
    return AdminService(user_repository=user_repository, jwt_service=jwt_service)
