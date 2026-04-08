from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status

from app.core.config import settings
from app.dependencies.services import AuthServiceDep
from app.models.users import UserModel


def _extract_bearer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header is missing',
        )
    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authorization header',
        )
    return token


async def get_access_token(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    return _extract_bearer_token(authorization)


AccessTokenDep = Annotated[str, Depends(get_access_token)]


async def get_refresh_token_from_cookie(
    refresh_token: Annotated[
        str | None,
        Cookie(alias=settings.jwt_refresh_cookie_name),
    ] = None,
) -> str:
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token is missing',
        )
    return refresh_token


RefreshTokenDep = Annotated[str, Depends(get_refresh_token_from_cookie)]


async def get_current_user(
    auth_service: AuthServiceDep,
    access_token: AccessTokenDep,
) -> UserModel:
    return await auth_service.get_current_user_by_access_token(access_token)


CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]
