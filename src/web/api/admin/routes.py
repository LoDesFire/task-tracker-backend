from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from src.app.services.admin_service import AdminService
from src.helpers.exceptions.service_exceptions.admin_exceptions import (
    AdminUserNotFoundException,
)
from src.helpers.jwt_helper import JWTTokenPayload
from src.schemas.admin_schemas import (
    GetUsersAdminSchema,
    OutputUserAdminSchema,
    OutputUsersAdminSchema,
    UpdateUserAdminSchema,
    UserIdAdminSchema,
)
from src.schemas.user_schemas import UsersIDType
from src.web.dependencies.auth_dependency import auth_dependency

from .dependencies import get_admin_service

admin_v1_router = APIRouter(prefix="/admin", tags=["Admin Actions"])


@admin_v1_router.get("/user", response_model=OutputUsersAdminSchema)
async def get_users(
    filters: Annotated[GetUsersAdminSchema, Query()],
    _: JWTTokenPayload = Depends(auth_dependency(is_admin=True)),
    admin_service: AdminService = Depends(get_admin_service),
):
    return await admin_service.get_filtered_users(filters)


@admin_v1_router.delete("/user/{user_id}", response_model=UserIdAdminSchema)
async def delete_user(
    user_id: UsersIDType,
    _: JWTTokenPayload = Depends(auth_dependency(is_admin=True)),
    admin_service: AdminService = Depends(get_admin_service),
):
    try:
        return await admin_service.delete_user(user_id)
    except AdminUserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc.user_error)
        )


@admin_v1_router.post(
    "/user/deactivate/{user_id}", response_model=OutputUserAdminSchema
)
async def deactivate_user(
    user_id: UsersIDType,
    _: JWTTokenPayload = Depends(auth_dependency(is_admin=True)),
    admin_service: AdminService = Depends(get_admin_service),
):
    try:
        return await admin_service.deactivate_user(user_id)
    except AdminUserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc.user_error)
        )


@admin_v1_router.put("/user/{user_id}", response_model=OutputUserAdminSchema)
async def update_user(
    user_id: UsersIDType,
    request_params: UpdateUserAdminSchema,
    _: JWTTokenPayload = Depends(auth_dependency(is_admin=True)),
    admin_service: AdminService = Depends(get_admin_service),
):
    try:
        return await admin_service.update_user(user_id, request_params)
    except AdminUserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc.user_error)
        )
