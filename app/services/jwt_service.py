from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings


class TokenType:
    ACCESS = 'access'
    REFRESH = 'refresh'


def _build_payload(
    user_id: UUID,
    expires_in_seconds: int,
    token_type: str,
) -> tuple[dict, str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=expires_in_seconds)
    jti = uuid4().hex

    payload = {
        'iat': int(now.timestamp()),
        'exp': int(expires_at.timestamp()),
        'sub': str(user_id),
        'jti': jti,
        'token_type': token_type,
    }
    return payload, jti, expires_at


def create_access_token(user_id: UUID) -> tuple[str, str, datetime]:
    payload, jti, expires_at = _build_payload(
        user_id=user_id,
        expires_in_seconds=settings.jwt_access_token_expire_seconds,
        token_type=TokenType.ACCESS,
    )
    token = jwt.encode(
        payload,
        settings.jwt_private_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, jti, expires_at


def create_refresh_token(user_id: UUID) -> tuple[str, str, datetime]:
    payload, jti, expires_at = _build_payload(
        user_id=user_id,
        expires_in_seconds=settings.jwt_refresh_token_expire_seconds,
        token_type=TokenType.REFRESH,
    )
    token = jwt.encode(
        payload,
        settings.jwt_private_key,
        algorithm=settings.jwt_algorithm,
    )
    return token, jti, expires_at


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_private_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as exc:
        raise ValueError('Invalid token') from exc


def validate_token_type(payload: dict, expected_token_type: str) -> None:
    token_type = payload.get('token_type')
    if token_type != expected_token_type:
        raise ValueError('Invalid token type')


def decode_access_token(token: str) -> dict:
    payload = decode_token(token)
    validate_token_type(payload, TokenType.ACCESS)
    return payload


def decode_refresh_token(token: str) -> dict:
    payload = decode_token(token)
    validate_token_type(payload, TokenType.REFRESH)
    return payload
