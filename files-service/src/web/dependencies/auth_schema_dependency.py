from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from starlette import status

from helpers.exceptions.helpers_exceptions import JWTDecodeException
from helpers.jwt_helper import JWTTokenPayload, decode_token


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(
            scheme_name="Access token",
            description="A JWT token used to authenticate requests. "
                        "Sent via the HTTP Authorization header with the 'Bearer ' prefix.",
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> JWTTokenPayload:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            try:
                decoded_token = decode_token(token=credentials.credentials)
            except (JWTDecodeException, ValidationError):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            return decoded_token
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
