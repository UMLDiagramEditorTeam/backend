from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.routers import InterfaceVerifiedDep, WindowVerifiedDep
from app.dependencies.services import InterfaceServiceDep
from app.models.interfaces import InterfaceCreate, InterfacePublic, InterfaceUpdate
from app.schemas.base import PaginatedResponse
from app.schemas.interfaces import InterfaceFilters

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость

router = APIRouter(
    prefix='/projects/{project_id}/windows/{window_id}/interfaces', tags=['Interfaces']
)


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def get_interfaces(
    window: WindowVerifiedDep,
    interface_service: InterfaceServiceDep,
    filters: Annotated[InterfaceFilters, Query()],
) -> PaginatedResponse[InterfacePublic]:
    interfaces = await interface_service.get_interfaces_public(window.id, filters)

    total = await interface_service.count_interfaces(window.id, filters)

    return PaginatedResponse(
        data=interfaces, total=total, page=filters.page, limit=filters.limit
    )


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_interface(
    window: WindowVerifiedDep,
    interface_create: InterfaceCreate,
    interface_service: InterfaceServiceDep,
) -> InterfacePublic:
    return await interface_service.create_interface(  # type: ignore[return-value]
        window_id=window.id, interface_create=interface_create
    )


@router.get(
    '/{interface_id}',
    status_code=status.HTTP_200_OK,
)
async def get_interface(
    interface: InterfaceVerifiedDep,
) -> InterfacePublic:
    return interface  # type: ignore[return-value]


@router.put(
    '/{interface_id}',
    status_code=status.HTTP_200_OK,
)
async def update_interface(
    interface: InterfaceUpdate,
    interface_update: InterfaceUpdate,
    interface_service: InterfaceServiceDep,
) -> InterfacePublic:
    return await interface_service.update_interface(interface.id, interface_update)  # type: ignore[return-value]


@router.delete(
    '/{interface_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_interface(
    interface: InterfaceVerifiedDep,
    interface_service: InterfaceServiceDep,
) -> None:
    await interface_service.delete_interface(interface.id)
