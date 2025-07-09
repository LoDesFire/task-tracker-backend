import jwt
from pydantic import BaseModel

from src.models.base import UsersIDType
from src.helpers.exceptions.helpers_exceptions import JWTDecodeException

from src.constants import JWTTokenType
from src.settings.general_settings import settings


class JWTTokenPayload(BaseModel):
    exp: int
    iat: int
    nbf: int
    app_id: str
    jwt_id: str
    sub: UsersIDType
    type: JWTTokenType
    is_admin: bool = False
    is_verified: bool = True


class JWTToken:
    def __init__(self, payload: JWTTokenPayload, token: str) -> None:
        self.__payload = payload
        self.__token = token

    @property
    def payload(self) -> JWTTokenPayload:
        return self.__payload

    @property
    def token(self) -> str:
        return self.__token

    def __str__(self):
        return self.__token


def decode_token(token: str) -> JWTTokenPayload:
    """
    Decode and validate JWT token
    :param token_type: type of decoded JWT token
    :param token: JWT string
    :return:
    Decoded and validated JWT token
    :raises JWTDecodeException
    """
    try:
        decoded_token = jwt.decode(
            token,
            options=dict(
                require=["exp", "iat", "app_id", "jwt_id", "nbf", "sub", "type"],
                verify_iat=True,
                verify_nbf=True,
                verify_exp=True,
            ),
            key=settings.jwt_public_key,
            algorithms=["RS256"],
        )
        if decoded_token["type"] != JWTTokenType.ACCESS:
            raise JWTDecodeException
    except jwt.InvalidTokenError as exc:
        raise JWTDecodeException from exc

    return JWTTokenPayload.model_validate(decoded_token)
