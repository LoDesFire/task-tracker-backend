from fastapi import APIRouter, Depends, HTTPException, status

from src.app.services.auth_service import AuthService
from src.helpers.exceptions.service_exceptions import (
    LoginException,
    RegistrationException,
)
from src.schemas import RegisterInputSchema
from src.schemas.auth_schemas import LoginSchema, RegistrationOutputSchema, TokensSchema

from .dependencies import get_user_service
from .schemas import UserEmailSchema, VerificationConfirmationSchema

auth_v1_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_v1_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationOutputSchema,
    response_model_exclude_defaults=True,
)
async def create_user(
    user_data: RegisterInputSchema,
    auth_service: AuthService = Depends(get_user_service),
):
    """Creates a new user account."""
    try:
        output = await auth_service.register_user(register_schema=user_data)
    except RegistrationException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc.user_error)
        )
    # TODO: Send email
    return output


@auth_v1_router.post("/login", response_model=TokensSchema)
async def create_token(
    login_schema: LoginSchema, auth_service: AuthService = Depends(get_user_service)
):
    """Authenticates a user and returns an access token."""
    try:
        tokens = await auth_service.login_user(login_schema)
    except LoginException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc.user_error)
        )

    return tokens


@auth_v1_router.post(
    "/password-reset",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_password_reset(
    login_schema: LoginSchema,
    auth_service: AuthService = Depends(get_user_service),
):
    """Initiates the password reset process for a user."""
    try:
        await auth_service.login_user(login_schema)
    except LoginException as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc.user_error)
        )


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
