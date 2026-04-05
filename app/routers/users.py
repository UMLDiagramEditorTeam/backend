from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.dependencies.services import UserServiceDep
from app.models.users import UserCreate, UserPublic, UserUpdate
from app.schemas.base import PaginatedResponse
from app.schemas.users import UserFilters

router = APIRouter(prefix='/users', tags=['Users'])


# TODO: add admin rights check (authorization)


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    responses={
        401: {'description': 'Отсутствует или невалидный токен аутентификации'},
        403: {'description': 'Доступ запрещен'},
    },
)
async def get_users(
    user_service: UserServiceDep, filters: Annotated[UserFilters, Query()]
) -> PaginatedResponse[UserPublic]:
    users = await user_service.get_users(filters)

    total = await user_service.count_users(filters)

    return PaginatedResponse(
        data=users,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_create: UserCreate, user_service: UserServiceDep
) -> UserPublic:
    return await user_service.create_user(user_create)


@router.get(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: UUID, user_service: UserServiceDep) -> Optional[UserPublic]:
    return await user_service.get_user(user_id)


@router.put('/{user_id}', status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    user_service: UserServiceDep,
) -> Optional[UserPublic]:
    return await user_service.update_user(user_update, user_id)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserServiceDep,
) -> None:
    await user_service.delete_user(user_id)
