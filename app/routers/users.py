from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Query, Security, status

from app.dependencies.rbac import CurrentUserWithScopesDep
from app.dependencies.services import UserServiceDep
from app.models.users import UserCreate, UserPublic, UserUpdate
from app.schemas.base import PaginatedResponse
from app.schemas.roles import UpdateUserRolesRequest
from app.schemas.users import UserFilters

router = APIRouter(prefix='/users', tags=['Users'])


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    responses={
        401: {'description': 'Отсутствует или невалидный токен аутентификации'},
        403: {'description': 'Доступ запрещен'},
    },
)
async def get_users(
    user_service: UserServiceDep,
    filters: Annotated[UserFilters, Query()],
    _: Annotated[object, Security(CurrentUserWithScopesDep, scopes=['users:list'])],
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
    user_create: UserCreate,
    user_service: UserServiceDep,
    _: Annotated[object, Security(CurrentUserWithScopesDep, scopes=['users:create'])],
) -> UserPublic:
    return await user_service.create_user(user_create)


@router.get(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: UUID,
    user_service: UserServiceDep,
    _: Annotated[object, Security(CurrentUserWithScopesDep, scopes=['users:read'])],
) -> Optional[UserPublic]:
    return await user_service.get_user(user_id)


@router.put('/{user_id}', status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    user_service: UserServiceDep,
    _: Annotated[object, Security(CurrentUserWithScopesDep, scopes=['users:update'])],
) -> Optional[UserPublic]:
    return await user_service.update_user(user_update, user_id)


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: UserServiceDep,
    _: Annotated[object, Security(CurrentUserWithScopesDep, scopes=['users:delete'])],
) -> None:
    await user_service.delete_user(user_id)


@router.patch(
    '/{user_id}/roles',
    status_code=status.HTTP_200_OK,
)
async def update_user_roles(
    user_id: UUID,
    request: UpdateUserRolesRequest,
    user_service: UserServiceDep,
    current_user: Annotated[
        object,
        Security(CurrentUserWithScopesDep, scopes=['users:update_roles']),
    ],
) -> UserPublic:
    user = await user_service.get_user(user_id)
    if user is None:
        raise ValueError('User not found')

    from app.services.rbac import RBACService  # local import to avoid cycles

    rbac_service = RBACService(
        user_service._UserService__user_repository._Repository__session
    )  # noqa: SLF001
    updated_user = await rbac_service.replace_user_roles(user, request.roles)
    return updated_user
