from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.routers import (
    ClassMethodVerifiedDep,
    ClassVerifiedDep,
    InterfaceMethodVerifiedDep,
    InterfaceVerifiedDep,
)
from app.dependencies.services import MethodServiceDep
from app.models.methods import MethodCreate, MethodPublic, MethodUpdate
from app.schemas.base import PaginatedResponse
from app.schemas.methods import MethodFilters

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость

class_methods_router = APIRouter(
    prefix='/projects/{project_id}/windows/{window_id}/classes/{class_id}/methods',
    tags=['Methods'],
)

interface_methods_router = APIRouter(
    prefix='/projects/{project_id}/windows/{window_id}/interfaces/{interface_id}/methods',
    tags=['Methods'],
)


@class_methods_router.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def get_class_methods(
    class_obj: ClassVerifiedDep,
    method_service: MethodServiceDep,
    filters: Annotated[MethodFilters, Query()],
) -> PaginatedResponse[MethodPublic]:

    methods = await method_service.get_methods_public(filters, class_id=class_obj.id)

    total = await method_service.count_methods(filters, class_id=class_obj.id)

    return PaginatedResponse(
        data=methods,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@class_methods_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_class_method(
    class_obj: ClassVerifiedDep,
    method_create: MethodCreate,
    method_service: MethodServiceDep,
) -> MethodPublic:

    return await method_service.create_method(method_create, class_id=class_obj.id)  # type: ignore[return-value]


@class_methods_router.get(
    '/{method_id}',
    status_code=status.HTTP_200_OK,
)
async def get_class_method(method: ClassMethodVerifiedDep) -> MethodPublic:

    return method  # type: ignore[return-value]


@class_methods_router.put(
    '/{method_id}',
    status_code=status.HTTP_200_OK,
)
async def update_class_method(
    method: ClassMethodVerifiedDep,
    method_update: MethodUpdate,
    method_service: MethodServiceDep,
) -> MethodPublic:

    return await method_service.update_method(method.id, method_update)  # type: ignore[return-value]


@class_methods_router.delete(
    '/{method_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_class_method(
    method: ClassMethodVerifiedDep,
    method_service: MethodServiceDep,
) -> None:

    await method_service.delete_method(method.id)


######################interface_methods_router######################


@interface_methods_router.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def get_interface_methods(
    interface: InterfaceVerifiedDep,
    method_service: MethodServiceDep,
    filters: Annotated[MethodFilters, Query()],
) -> PaginatedResponse[MethodPublic]:

    methods = await method_service.get_methods_public(
        filters, interface_id=interface.id
    )

    total = await method_service.count_methods(filters, interface_id=interface.id)

    return PaginatedResponse(
        data=methods,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@interface_methods_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_interface_method(
    interface: InterfaceVerifiedDep,
    method_create: MethodCreate,
    method_service: MethodServiceDep,
) -> MethodPublic:

    return await method_service.create_method(method_create, interface_id=interface.id)  # type: ignore[return-value]


@interface_methods_router.get(
    '/{method_id}',
    status_code=status.HTTP_200_OK,
)
async def get_interface_method(method: InterfaceMethodVerifiedDep) -> MethodPublic:

    return method  # type: ignore[return-value]


@interface_methods_router.put(
    '/{method_id}',
    status_code=status.HTTP_200_OK,
)
async def update_interface_method(
    method: InterfaceMethodVerifiedDep,
    method_update: MethodUpdate,
    method_service: MethodServiceDep,
) -> MethodPublic:

    return await method_service.update_method(method.id, method_update)  # type: ignore[return-value]


@interface_methods_router.delete(
    '/{method_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_interface_method(
    method: InterfaceMethodVerifiedDep,
    method_service: MethodServiceDep,
) -> None:

    await method_service.delete_method(method.id)
