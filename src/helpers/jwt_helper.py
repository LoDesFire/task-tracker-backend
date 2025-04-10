import datetime
import uuid
from typing import Any

import jwt
from pydantic import BaseModel

from src.constants import JWTTokenType
from src.helpers.exceptions.helpers_exceptions import JWTDecodeException
from src.schemas.auth_schemas import JWTPayloadUserSchema
from src.settings.general_settings import settings


class JWTTokenPayload(BaseModel):
    exp: int
    iat: int
    nbf: int
    app_id: str
    jwt_id: str
    sub: str
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


def __sign_token(
    token_type: JWTTokenType,
    subject: str,
    payload: dict[str, Any] | None = None,
    ttl: datetime.timedelta = datetime.timedelta(minutes=1),
) -> JWTToken:
    """

    :param token_type: objects of JWTTokenType
    :param subject: user's id email in the database
    :param payload: email, roles, flags, etc.
    :param ttl: time to live
    :return:
    Signed JWT
    """
    if payload is None:
        payload = {}

    current_timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
    nbf = int(payload["nbf"]) if payload.get("nbf", None) else current_timestamp
    data = dict(
        type=token_type,
        iat=current_timestamp,
        sub=subject,
        app_id=(
            str(uuid.uuid4())
            if payload.get("app_id", None) is None
            else payload["app_id"]
        ),  # jwt's family unique id, used for revoking tokens family
        jwt_id=str(uuid.uuid4()),
        nbf=nbf,
    )
    data.update(dict(exp=nbf + int(ttl.total_seconds())))

    payload.update(data)
    signed_token = jwt.encode(
        payload=payload,
        key=settings.jwt_settings.secret.get_secret_value(),
        algorithm="HS256",
    )
    return JWTToken(payload=JWTTokenPayload.model_validate(payload), token=signed_token)


def decode_token(token: str, token_type: JWTTokenType) -> JWTTokenPayload:
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
            key=settings.jwt_settings.secret.get_secret_value(),
            algorithms=["HS256"],
        )
        if decoded_token["type"] != token_type:
            raise JWTDecodeException
    except jwt.InvalidTokenError as exc:
        raise JWTDecodeException from exc

    return JWTTokenPayload.model_validate(decoded_token)


def create_access_token(subject: str, jwt_payload: JWTPayloadUserSchema) -> JWTToken:
    """
    Create access token
    :param subject: user's email in the database
    :param jwt_payload: email, roles, flags, etc.
    :return:
    Access token
    """
    return __sign_token(
        token_type=JWTTokenType.ACCESS,
        subject=subject,
        payload=jwt_payload.model_dump(exclude_defaults=True) if jwt_payload else None,
        ttl=datetime.timedelta(minutes=settings.jwt_settings.access_token_ttl_minutes),
    )


def create_refresh_token(subject: str, app_id: str | None = None) -> JWTToken:
    """
    Create refresh token
    :param app_id: ID of the tokens family
    :param subject: user's email in the database
    :return:
    Refresh token
    """
    return __sign_token(
        token_type=JWTTokenType.REFRESH,
        subject=subject,
        payload=dict(app_id=app_id),
        ttl=datetime.timedelta(minutes=settings.jwt_settings.refresh_token_ttl_minutes),
    )
