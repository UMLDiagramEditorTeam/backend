from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.dependencies.services import ProjectServiceDep
from app.models import ProjectCreate, ProjectPublic, ProjectUpdate
from app.routers import ProjectVerifiedDep
from app.schemas import PaginatedResponse, ProjectFilters

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость

router = APIRouter(prefix='/projects', tags=['Projects'])


@router.get('/', status_code=status.HTTP_200_OK)
async def get_projects(
    project_service: ProjectServiceDep,
    filters: Annotated[ProjectFilters, Query()],
) -> PaginatedResponse[ProjectPublic]:
    # TODO: get user_id from jwt

    projects = await project_service.get_projects(filters)

    total = await project_service.count_projects(filters)

    return PaginatedResponse(
        data=projects, total=total, page=filters.page, limit=filters.limit
    )


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_project(
    project_create: ProjectCreate,
    project_service: ProjectServiceDep,
    user_id: UUID,  # TODO: remove after adding authorization
) -> ProjectPublic:
    return await project_service.create_project(project_create, user_id)


@router.get(
    '/{project_id}',
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project: ProjectVerifiedDep,
) -> ProjectPublic:
    return project


@router.put(
    '/{project_id}',
    status_code=status.HTTP_201_CREATED,
)
async def update_project(
    project: ProjectVerifiedDep,
    project_update: ProjectUpdate,
    project_service: ProjectServiceDep,
) -> ProjectPublic:

    return await project_service.update_project(project.id, project_update)


@router.delete(
    '/{project_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project: ProjectVerifiedDep,
    project_service: ProjectServiceDep,
) -> None:

    await project_service.delete_project(project.id)
