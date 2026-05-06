from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies.auth import CurrentUserDep
from app.dependencies.routers import ProjectVerifiedDep
from app.dependencies.services import ProjectServiceDep
from app.models import ProjectCreate, ProjectPublic, ProjectUpdate
from app.schemas import PaginatedResponse, ProjectFilters

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость

router = APIRouter(prefix='/projects', tags=['Projects'])


@router.get('/', status_code=status.HTTP_200_OK)
async def get_projects(
    project_service: ProjectServiceDep,
    current_user: CurrentUserDep,
    filters: Annotated[ProjectFilters, Query()],
) -> PaginatedResponse[ProjectPublic]:
    projects = await project_service.get_projects(filters, user_id=current_user.id)

    total = await project_service.count_projects(filters, user_id=current_user.id)

    return PaginatedResponse(
        data=projects,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_project(
    project_create: ProjectCreate,
    project_service: ProjectServiceDep,
    current_user: CurrentUserDep,
) -> ProjectPublic:
    return await project_service.create_project(project_create, current_user.id)


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
    status_code=status.HTTP_200_OK,
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
