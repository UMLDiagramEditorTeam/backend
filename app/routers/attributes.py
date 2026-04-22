from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.routers import AttributeVerifiedDep, ClassVerifiedDep
from app.dependencies.services import AttributeServiceDep
from app.models.attributes import AttributeCreate, AttributeModel, AttributeUpdate
from app.schemas.attributes import AttributeFilters
from app.schemas.base import PaginatedResponse

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость

router = APIRouter(
    prefix='/classes/{class_id}/attributes',
    tags=['Attributes'],
)


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def get_attributes(
    class_obj: ClassVerifiedDep,
    attribute_service: AttributeServiceDep,
    filters: Annotated[AttributeFilters, Query()],
) -> PaginatedResponse[AttributeModel]:
    attributes = await attribute_service.get_attributes(class_obj.id, filters)

    total = await attribute_service.count_attributes(class_obj.id, filters)

    return PaginatedResponse(
        data=attributes,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_attribute(
    class_obj: ClassVerifiedDep,
    attribute_create: AttributeCreate,
    attribute_service: AttributeServiceDep,
) -> AttributeModel:
    return await attribute_service.create_attribute(attribute_create, class_obj.id)


@router.get(
    '/{attribute_id}',
    status_code=status.HTTP_200_OK,
)
async def get_attribute(
    attribute: AttributeVerifiedDep,
) -> AttributeModel:
    return attribute


@router.put(
    '/{attribute_id}',
    status_code=status.HTTP_200_OK,
)
async def update_attribute(
    attribute: AttributeVerifiedDep,
    attribute_update: AttributeUpdate,
    attribute_service: AttributeServiceDep,
) -> AttributeModel:
    return await attribute_service.update_attribute(attribute.id, attribute_update)


@router.delete(
    '/{attribute_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_attribute(
    attribute: AttributeVerifiedDep,
    attribute_service: AttributeServiceDep,
) -> None:
    await attribute_service.delete_attribute(attribute.id)
