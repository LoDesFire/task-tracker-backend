from fastapi import APIRouter, Depends, status

from app.schemas.auth_schemas import (
    LoginUserSchema,
    RegisterUserSchema,
    UserEmailSchema,
    VerificationConfirmationSchema,
)
from app.services.auth_service import AuthService

from .dependencies import get_user_service

auth_v1_router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


@auth_v1_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: RegisterUserSchema, auth_service: AuthService = Depends(get_user_service)
):
    """Creates a new user account."""
    pass


@auth_v1_router.post(
    "/login",
)
async def create_token(
    login_data: LoginUserSchema, auth_service: AuthService = Depends(get_user_service)
):
    """Authenticates a user and returns an access token."""
    pass


@auth_v1_router.post(
    "/password-reset",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_password_reset(
    reset_request_data: UserEmailSchema,
    auth_service: AuthService = Depends(get_user_service),
):
    """Initiates the password reset process for a user."""
    pass


@auth_v1_router.post("/verification", status_code=status.HTTP_202_ACCEPTED)
async def request_verification(
    verification_request_data: UserEmailSchema,
    auth_service: AuthService = Depends(get_user_service),
):
    """Initiates the account verification process."""
    pass


@auth_v1_router.post(
    "/verification/confirmation", status_code=status.HTTP_204_NO_CONTENT
)
async def confirm_verification(
    confirmation_data: VerificationConfirmationSchema,
    auth_service: AuthService = Depends(get_user_service),
):
    """Confirms account verification using a provided token."""
    pass
