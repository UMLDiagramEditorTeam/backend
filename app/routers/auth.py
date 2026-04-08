from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.dependencies.auth import CurrentUserDep, RefreshTokenDep
from app.dependencies.services import AuthServiceDep
from app.models.users import UserCreate, UserPublic
from app.schemas.auth import LoginRequest, SuccessResponse, TokenPairResponse

router = APIRouter(prefix='/auth', tags=['Auth'])


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.jwt_refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.jwt_refresh_cookie_secure,
        samesite=settings.jwt_refresh_cookie_samesite,
        path=settings.jwt_refresh_cookie_path,
        domain=settings.jwt_refresh_cookie_domain,
        expires=int(
            (
                datetime.now(timezone.utc)
                + timedelta(seconds=settings.jwt_refresh_token_expire_seconds)
            ).timestamp()
        ),
    )


def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.jwt_refresh_cookie_name,
        path=settings.jwt_refresh_cookie_path,
        domain=settings.jwt_refresh_cookie_domain,
    )


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,
)
async def register(
    user_create: UserCreate,
    auth_service: AuthServiceDep,
) -> UserPublic:
    user = await auth_service.register(user_create)
    return user


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_model=TokenPairResponse,
)
async def login(
    login_request: LoginRequest,
    response: Response,
    auth_service: AuthServiceDep,
) -> TokenPairResponse:
    auth_result = await auth_service.login(
        email=login_request.email,
        password=login_request.password,
    )
    set_refresh_cookie(response, auth_result['refresh_token'])
    return TokenPairResponse(
        access_token=auth_result['access_token'],
        refresh_token=auth_result['refresh_token'],
    )


@router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
async def me(current_user: CurrentUserDep) -> UserPublic:
    return current_user


@router.post(
    '/logout',
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse,
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
    response_model=TokenPairResponse,
)
async def refresh(
    response: Response,
    refresh_token: RefreshTokenDep,
    auth_service: AuthServiceDep,
) -> TokenPairResponse:
    auth_result = await auth_service.refresh(refresh_token)
    set_refresh_cookie(response, auth_result['refresh_token'])
    return TokenPairResponse(
        access_token=auth_result['access_token'],
        refresh_token=auth_result['refresh_token'],
    )
