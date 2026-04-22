from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.routers import ClassVerifiedDep, WindowVerifiedDep
from app.dependencies.services import ClassServiceDep
from app.models.classes import ClassCreate, ClassPublic, ClassUpdate
from app.schemas.base import PaginatedResponse
from app.schemas.classes import ClassFilters

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость

router = APIRouter(prefix='/windows/{window_id}/classes', tags=['Classes'])


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def get_classes(
    window: WindowVerifiedDep,
    class_service: ClassServiceDep,
    filters: Annotated[ClassFilters, Query()],
) -> PaginatedResponse[ClassPublic]:
    classes = await class_service.get_classes_public(window.id, filters)

    total = await class_service.count_classes(window.id, filters)

    return PaginatedResponse(
        data=classes,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_class(
    window: WindowVerifiedDep,
    class_create: ClassCreate,
    class_service: ClassServiceDep,
) -> ClassPublic:
    return await class_service.create_class(  # type: ignore[return-value]
        class_create,
        window_id=window.id,
    )


@router.get(
    '/{class_id}',
    status_code=status.HTTP_200_OK,
)
async def get_class(
    class_obj: ClassVerifiedDep,
) -> ClassPublic:
    return class_obj  # type: ignore[return-value]


@router.put(
    '/{class_id}',
    status_code=status.HTTP_200_OK,
)
async def update_class(
    class_obj: ClassVerifiedDep,
    class_update: ClassUpdate,
    class_service: ClassServiceDep,
) -> ClassPublic:
    return await class_service.update_class(class_obj.id, class_update)  # type: ignore[return-value]


@router.delete(
    '/{class_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_class(
    class_obj: ClassVerifiedDep,
    class_service: ClassServiceDep,
) -> None:
    await class_service.delete_class(class_obj.id)
