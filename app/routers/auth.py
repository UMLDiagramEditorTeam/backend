from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.dependencies.auth import AuthServiceDep, CurrentUserDep, RefreshTokenDep
from app.models.users import UserCreate, UserPublic
from app.schemas.auth import SuccessResponse, TokenResponse

router = APIRouter(prefix='/auth', tags=['Auth'])


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.auth.jwt_refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.auth.jwt_refresh_cookie_secure,
        samesite=settings.auth.jwt_refresh_cookie_samesite,
        path=settings.auth.jwt_refresh_cookie_path,
        expires=int(
            (
                datetime.now(timezone.utc) + settings.auth.jwt_refresh_token_expire
            ).timestamp()
        ),
    )


def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth.jwt_refresh_cookie_name,
        path=settings.auth.jwt_refresh_cookie_path,
    )


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_create: UserCreate,
    auth_service: AuthServiceDep,
) -> UserPublic:
    return await auth_service.register(user_create)


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
)
async def login(
    auth_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    tokens = await auth_service.login(
        email=auth_data.username,
        password=auth_data.password,
    )

    set_refresh_cookie(response, tokens.refresh_token)

    return TokenResponse(
        access_token=tokens.access_token,
    )


@router.get(
    '/me',
    status_code=status.HTTP_200_OK,
)
async def me(current_user: CurrentUserDep) -> UserPublic:
    return current_user


@router.post(
    '/logout',
    status_code=status.HTTP_200_OK,
)
async def logout(
    response: Response,
    refresh_token: RefreshTokenDep,
    auth_service: AuthServiceDep,
) -> SuccessResponse:
    await auth_service.logout(refresh_token)
    delete_refresh_cookie(response)
    return SuccessResponse(success=True)


@router.post(
    '/refresh',
    status_code=status.HTTP_200_OK,
)
async def refresh(
    response: Response,
    refresh_token: RefreshTokenDep,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    tokens = await auth_service.refresh(refresh_token)

    set_refresh_cookie(response, tokens.refresh_token)

    return TokenResponse(
        access_token=tokens.access_token,
    )
