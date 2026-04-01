from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.services import RelationServiceDep
from app.models.relations import RelationCreate, RelationPublic, RelationUpdate
from app.routers import RelationVerifiedDep, WindowVerifiedDep
from app.schemas.base import PaginatedResponse
from app.schemas.relations import RelationFilters

router = APIRouter(
    prefix='/projects/{project_id}/windows/{window_id}/relations', tags=['Relations']
)

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def get_relations(
    window: WindowVerifiedDep,
    relation_service: RelationServiceDep,
    filters: Annotated[RelationFilters, Query()],
) -> PaginatedResponse[RelationPublic]:

    relations = await relation_service.get_relations(window.id, filters)

    total = await relation_service.count_relations(window.id, filters)

    return PaginatedResponse(
        data=relations,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_relation(
    window: WindowVerifiedDep,
    relation_create: RelationCreate,
    relation_service: RelationServiceDep,
) -> RelationPublic:

    return await relation_service.create_relation(window.id, relation_create)


@router.get(
    '/{relation_id}',
    status_code=status.HTTP_200_OK,
)
async def get_relation(
    relation: RelationVerifiedDep,
) -> RelationPublic:

    return relation


@router.put(
    '/{relation_id}',
    status_code=status.HTTP_200_OK,
)
async def update_relation(
    relation: RelationVerifiedDep,
    relation_update: RelationUpdate,
    relation_service: RelationServiceDep,
) -> RelationPublic:

    return await relation_service.update_relation(relation.id, relation_update)


@router.delete(
    '/{relation_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_relation(
    relation: RelationVerifiedDep,
    relation_service: RelationServiceDep,
) -> None:

    await relation_service.delete_relation(relation.id)
