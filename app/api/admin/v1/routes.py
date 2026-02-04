from typing import Annotated

from fastapi import APIRouter, Query

from .schemas import GetUserByIdSchema, GetUsersSchema, UpdateUserByIdSchema

admin_v1_router = APIRouter(prefix="/v1/admin", tags=["Admin Actions"])


@admin_v1_router.get("/user")
def get_users(
    request_params: Annotated[GetUsersSchema, Query()],
    # get admin dependency
):
    pass


@admin_v1_router.delete("/user")
def delete_user(
    request_params: GetUserByIdSchema,
    # get admin dependency
):
    pass


@admin_v1_router.put("/user")
def update_user(
    request_params: UpdateUserByIdSchema,
    # get admin dependency
):
    pass
