from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette import status

from src.app.services.user_service import UserService
from src.helpers.exceptions.service_exceptions.user_exceptions import (
    UserNotFoundException,
    UserServiceException,
)
from src.helpers.jwt_helper import JWTTokenPayload
from src.schemas.user_schemas import (
    PasswordSchema,
    UpdateEmailUserSchema,
    UpdatePasswordUserSchema,
    UpdateUserSchema,
    UserOutputSchema,
)
from src.web.api.user.dependencies import get_user_service
from src.web.dependencies.auth_dependency import auth_dependency

user_v1_router = APIRouter(prefix="/user", tags=["User Actions"])


@user_v1_router.put("/", response_model=UserOutputSchema)
async def update_user(
    update_schema: UpdateUserSchema,
    auth_context: JWTTokenPayload = Depends(auth_dependency()),
    user_service: UserService = Depends(get_user_service),
):
    try:
        return await user_service.update_user(auth_context, update_schema)
    except UserServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc.user_error),
        )


@user_v1_router.get("/", response_model=UserOutputSchema)
async def get_user(
    auth_context: JWTTokenPayload = Depends(auth_dependency()),
    user_service: UserService = Depends(get_user_service),
):
    try:
        return await user_service.get_user(auth_context)
    except UserServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc.user_error),
        )


@user_v1_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    password_schema: PasswordSchema,
    auth_context: JWTTokenPayload = Depends(auth_dependency(is_verified=False)),
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.delete_user(password_schema.password, auth_context)
    except UserServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc.user_error),
        )


@user_v1_router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(
    password_schema: UpdatePasswordUserSchema,
    auth_context: JWTTokenPayload = Depends(auth_dependency(is_verified=False)),
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.update_password(auth_context, password_schema)
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc.user_error),
        )
    except UserServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc.user_error),
        )


@user_v1_router.put("/email", status_code=status.HTTP_202_ACCEPTED)
async def update_email(
    email_schema: UpdateEmailUserSchema,
    auth_context: JWTTokenPayload = Depends(auth_dependency(is_verified=False)),
    user_service: UserService = Depends(get_user_service),
):
    try:
        await user_service.update_email(email_schema, auth_context)
    except UserNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc.user_error),
        )
    except UserServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc.user_error),
        )
