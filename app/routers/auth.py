from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.dependencies.auth import AuthServiceDep, CurrentUserDep, RefreshTokenDep
from app.models.users import UserCreate, UserPublic
from app.schemas.auth import (
    AccountConfirmationRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    SuccessResponse,
    TokenResponse,
)

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
    status_code=status.HTTP_200_OK,
)
async def register(
    user_create: UserCreate,
    background_tasks: BackgroundTasks,
    auth_service: AuthServiceDep,
) -> UserPublic:
    return await auth_service.register(user_create, background_tasks)


@router.post(
    '/confirm-account',
    status_code=status.HTTP_200_OK,
)
async def confirm_account(
    request: AccountConfirmationRequest,
    auth_service: AuthServiceDep,
) -> UserPublic:
    return await auth_service.confirm_account(
        user_id=request.user_id,
        code=request.code,
    )


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


@router.post(
    '/password/reset',
    status_code=status.HTTP_200_OK,
)
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthServiceDep,
) -> SuccessResponse:
    await auth_service.request_password_reset(request.email, background_tasks)
    return SuccessResponse(success=True)


@router.post(
    '/password/change',
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: PasswordChangeRequest,
    auth_service: AuthServiceDep,
) -> SuccessResponse:
    await auth_service.change_password(request)
    return SuccessResponse(success=True)
