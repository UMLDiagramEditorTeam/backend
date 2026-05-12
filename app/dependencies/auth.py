from typing import Annotated

from fastapi import Cookie, Depends

from app.core.config import settings
from app.core.errors import UnauthorizedError
from app.core.security import oauth2_scheme
from app.models.users import UserModel
from app.services.auth import AuthService

AccessTokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_refresh_token_from_cookie(
    refresh_token: Annotated[
        str | None,
        Cookie(alias=settings.auth.jwt_refresh_cookie_name),
    ] = None,
) -> str:
    if refresh_token is None:
        raise UnauthorizedError(message='Отсутствует refresh-токен')
    return refresh_token


RefreshTokenDep = Annotated[str, Depends(get_refresh_token_from_cookie)]

AuthServiceDep = Annotated[AuthService, Depends(AuthService)]


async def get_current_user(
    auth_service: AuthServiceDep,
    access_token: AccessTokenDep,
) -> UserModel:
    return await auth_service.get_current_user_by_access_token(access_token)


CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]
