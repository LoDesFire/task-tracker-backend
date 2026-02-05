from fastapi import APIRouter, Depends, HTTPException, status

from src.app.services.auth_service import AuthService
from src.constants import RevokeTokensScope
from src.helpers.exceptions.service_exceptions import AuthServiceException
from src.helpers.jwt_helper import JWTTokenPayload
from src.schemas import RegisterInputSchema
from src.schemas.auth_schemas import (
    LoginSchema,
    RefreshTokenSchema,
    RegistrationOutputSchema,
    TokensSchema,
    VerificationConfirmationSchema,
)
from src.web.dependencies.auth_dependency import auth_dependency

from .dependencies import get_auth_service

auth_v1_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_v1_router.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationOutputSchema,
    response_model_exclude_defaults=True,
)
async def create_user(
    user_data: RegisterInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Creates a new user account."""
    try:
        output = await auth_service.register_user(register_schema=user_data)
    except AuthServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc.user_error),
        )
    return output


@auth_v1_router.post("/login", response_model=TokensSchema)
async def create_token(
    login_schema: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticates a user and returns an access token."""
    try:
        tokens = await auth_service.login_user(login_schema)
    except AuthServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc.user_error),
        )
    return tokens


@auth_v1_router.post("/tokens/refresh", response_model=TokensSchema)
async def refreshes_tokens(
    refresh_token_schema: RefreshTokenSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh access tokens."""
    try:
        tokens = await auth_service.refresh_user_tokens(refresh_token_schema)
    except AuthServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc.user_error),
        )
    return tokens


@auth_v1_router.post("/tokens/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_tokens(
    scope: RevokeTokensScope,
    auth_context: JWTTokenPayload = Depends(auth_dependency()),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Revoke tokens."""
    try:
        await auth_service.revoke_user_tokens(auth_context, scope)
    except AuthServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc.user_error),
        )


@auth_v1_router.post(
    "/password-reset",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_password_reset(
    auth_context: JWTTokenPayload = Depends(auth_dependency()),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Initiates the password reset process for a user."""
    try:
        await auth_service.reset_password(auth_context)
    except AuthServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc.user_error),
        )


@auth_v1_router.post("/verification", status_code=status.HTTP_204_NO_CONTENT)
async def request_verification(
    auth_context: JWTTokenPayload = Depends(auth_dependency(is_verified=False)),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Initiates the account verification process."""
    try:
        await auth_service.send_verification_code(auth_context)
    except AuthServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc.user_error),
        )


@auth_v1_router.post(
    "/verification/confirmation", status_code=status.HTTP_204_NO_CONTENT
)
async def confirm_verification(
    confirmation_data: VerificationConfirmationSchema,
    auth_context: JWTTokenPayload = Depends(auth_dependency(is_verified=False)),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Confirms account verification using a provided token."""
    try:
        await auth_service.confirm_verification_code(
            confirmation_data.confirmation_code,
            auth_context,
        )
    except AuthServiceException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc.user_error),
        )
