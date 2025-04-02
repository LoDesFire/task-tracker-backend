import datetime
import uuid
from typing import Any

import jwt

from src.constants import JWTTokenType
from src.helpers.exceptions.helpers_exceptions import JWTDecodeException
from src.schemas.auth_schemas import JWTPayloadUserSchema
from src.settings.general_settings import settings


def __sign_token(
    token_type: JWTTokenType,
    subject: str,
    payload: dict[str, Any] | None = None,
    ttl: datetime.timedelta = datetime.timedelta(minutes=1),
):
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
        fam_id=str(
            uuid.uuid4()
        ),  # jwt's family unique id, used for revoking tokens family
        nbf=nbf,
    )
    data.update(dict(exp=nbf + int(ttl.total_seconds())))

    payload.update(data)

    return jwt.encode(
        payload=payload,
        key=settings.jwt_settings.secret.get_secret_value(),
        algorithm="HS256",
    )


def decode_token(token: str) -> dict[str, str]:
    """
    Decode and validate JWT token
    :param token: JWT string
    :return:
    Decoded and validated JWT token
    :raises JWTDecodeException
    """
    try:
        return jwt.decode(
            token,
            options=dict(
                require=["exp", "iat", "fam_id", "nbf", "sub", "type"],
                verify_iat=True,
                verify_nbf=True,
                verify_exp=True,
            ),
            key=settings.jwt_settings.secret.get_secret_value(),
            algorithms=["HS256"],
        )
    except jwt.InvalidTokenError as e:
        raise JWTDecodeException from e


def create_access_token(subject: str, jwt_payload: JWTPayloadUserSchema | None):
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
        ttl=datetime.timedelta(
            minutes=settings.jwt_settings.access_token_expiration_minutes
        ),
    )


def create_refresh_token(subject: str):
    """
    Create refresh token
    :param subject: user's email in the database
    :return:
    Refresh token
    """
    return __sign_token(
        token_type=JWTTokenType.REFRESH,
        subject=subject,
        ttl=datetime.timedelta(
            minutes=settings.jwt_settings.refresh_token_expiration_minutes
        ),
    )
