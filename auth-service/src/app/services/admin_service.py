from src.app.repositories import UserRepository
from src.app.services.jwt_service import JWTService
from src.helpers.exceptions.repository_exceptions import (
    RepositoryIntegrityException,
    RepositoryNotFoundException,
)
from src.helpers.exceptions.service_exceptions.admin_exceptions import (
    AdminServiceException,
    AdminUserNotFoundException,
)
from src.schemas.admin_schemas import GetUsersAdminSchema, UpdateUserAdminSchema
from src.schemas.user_schemas import UsersIDType


class AdminService:
    def __init__(self, user_repository: UserRepository, jwt_service: JWTService):
        self.user_repo = user_repository
        self.jwt_service = jwt_service

    async def get_filtered_users(self, users_filter_schema: GetUsersAdminSchema):
        filters_dict = users_filter_schema.filters()

        search_result = await self.user_repo.search(
            filters_dict,
            users_filter_schema.sort_by,
            page_number=users_filter_schema.page,
            page_size=users_filter_schema.page_size,
        )

        return {
            "users": search_result.items,
            "current_page": search_result.page_number,
            "total_pages": search_result.page_count,
            "total_items": search_result.total_items_count,
        }

    async def update_user(
        self,
        user_id: UsersIDType,
        update_user_schema: UpdateUserAdminSchema,
    ):
        try:
            await self.user_repo.get_by_id(user_id)
        except RepositoryNotFoundException as exc:
            raise AdminUserNotFoundException(
                f"User with id {user_id} not found"
            ) from exc

        return await self.user_repo.update(
            user_id,
            **update_user_schema.model_dump(exclude_defaults=True),
        )

    async def deactivate_user(self, user_id: UsersIDType):
        try:
            await self.user_repo.get_by_id(user_id)
        except RepositoryNotFoundException as exc:
            raise AdminUserNotFoundException(
                f"User with id {user_id} not found"
            ) from exc

        await self.jwt_service.revoke_all_tokens(user_id)
        return await self.user_repo.update(user_id, **dict(is_active=False))

    async def delete_user(self, user_id: UsersIDType):
        try:
            await self.user_repo.get_by_id(user_id)
        except RepositoryNotFoundException as exc:
            raise AdminUserNotFoundException(
                f"User with id {user_id} not found"
            ) from exc

        await self.jwt_service.revoke_all_tokens(user_id)
        try:
            deleted_user_id = await self.user_repo.delete(user_id)
        except RepositoryIntegrityException as exc:
            raise AdminServiceException("Internal error") from exc

        return {"id": deleted_user_id}
