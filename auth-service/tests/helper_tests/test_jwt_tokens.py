import datetime
import uuid

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from freezegun import freeze_time

from src.constants import JWTTokenType
from src.helpers.exceptions.helpers_exceptions import JWTDecodeException
from src.helpers.jwt_helper import (
    __sign_token,
    decode_token,
)

rsa_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

another_rsa_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Фиктивные настройки для тестов
TEST_JWT_PRIVATE_KEY = rsa_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
TEST_JWT_PUBLIC_KEY = rsa_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
TEST_ACCESS_TTL = 15  # минут
TEST_REFRESH_TTL = 1440  # минут


@pytest.fixture
def mock_settings(mocker):
    """Мокируем settings.jwt_settings."""
    mock = mocker.patch("src.helpers.jwt_helper.settings")
    mock.jwt_settings.private_key.get_secret_value.return_value = TEST_JWT_PRIVATE_KEY
    mock.jwt_settings.public_key = TEST_JWT_PUBLIC_KEY
    mock.jwt_settings.access_token_expiration_minutes = TEST_ACCESS_TTL
    mock.jwt_settings.refresh_token_expiration_minutes = TEST_REFRESH_TTL
    return mock


def test_successful_token_sign(mock_settings):
    """Checks successful JWT signing and verifying process"""
    with freeze_time("2023-01-01 00:00:00"):
        token = __sign_token(JWTTokenType.ACCESS, uuid.uuid4())

        # Проверяем, что были обращения к моковым настройкам
        mock_settings.jwt_settings.private_key.get_secret_value.assert_called_once()

        decode_token(token.token, JWTTokenType.ACCESS)


def test_unsuccessful_token_sign(mock_settings):
    """Checks unsuccessful JWT verifying process"""
    with freeze_time("2023-01-01 00:00:00"):
        token = __sign_token(JWTTokenType.ACCESS, uuid.uuid4())

        # Проверяем, что были обращения к моковым настройкам
        mock_settings.jwt_settings.private_key.get_secret_value.assert_called_once()

        # Подменяем секрет на чужой
        mock_settings.jwt_settings.public_key = (
            another_rsa_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

        with pytest.raises(JWTDecodeException):
            decode_token(token.token, JWTTokenType.ACCESS)


def test_jwt_data_integrity_with_overriding(mock_settings):
    """Checks JWT data integrity with overriding"""
    with freeze_time("2023-01-01 00:00:00"):
        current_timestamp = int(
            datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )
        nbf = current_timestamp - datetime.timedelta(seconds=59).seconds

        token = __sign_token(
            JWTTokenType.ACCESS,
            uuid.uuid4(),
            payload={"random_data": 123, "app_id": "test_app_id", "nbf": nbf},
            ttl=datetime.timedelta(minutes=1),
        )

        mock_settings.jwt_settings.private_key.get_secret_value.assert_called_once()

        decoded_token = decode_token(token.token, token_type=JWTTokenType.ACCESS)
        with pytest.raises(AttributeError):
            assert decoded_token.random_data != 123
        assert decoded_token.app_id == "test_app_id"
        assert decoded_token.nbf == nbf


#
def test_jwt_data_integrity(mock_settings):
    """Checks JWT data integrity"""
    with freeze_time("2023-01-01 00:00:00"):
        current_timestamp = int(
            datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )
        token = __sign_token(
            JWTTokenType.ACCESS, uuid.uuid4(), payload={"random_data": 123}
        )

        mock_settings.jwt_settings.private_key.get_secret_value.assert_called_once()

        decoded_token = decode_token(token.token, JWTTokenType.ACCESS)
        uuid.UUID(decoded_token.app_id)

        with pytest.raises(AttributeError):
            assert decoded_token.random_data != 123

        assert decoded_token.nbf == current_timestamp


def test_decode_token_invalid(mock_settings):
    """Проверяем обработку невалидного токена."""
    invalid_token = "invalid.token.here"
    with pytest.raises(JWTDecodeException):
        decode_token(invalid_token, JWTTokenType.ACCESS)


def test_jwt_data_nbf(mock_settings):
    """Checks JWT data integrity with overriding"""
    with freeze_time("2023-01-01 00:00:00"):
        current_timestamp = int(
            datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        )
        nbf = current_timestamp - datetime.timedelta(seconds=60).seconds

        token = __sign_token(
            JWTTokenType.ACCESS,
            uuid.uuid4(),
            payload={"nbf": nbf},
            ttl=datetime.timedelta(minutes=1),
        )

        mock_settings.jwt_settings.private_key.get_secret_value.assert_called_once()

        with pytest.raises(JWTDecodeException):
            decode_token(token.token, JWTTokenType.ACCESS)
