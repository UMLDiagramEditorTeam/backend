import json
from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.dependencies.code_generation import CodeGenerationServiceDep
from app.dependencies.routers import ProjectVerifiedDep, WindowVerifiedDep
from app.dependencies.services import WindowServiceDep
from app.models.windows import WindowCreate, WindowPublic, WindowUpdate
from app.schemas.base import PaginatedResponse
from app.schemas.windows import WindowFilters
from app.services.code_generation import TargetLanguage

router = APIRouter(prefix='/projects/{project_id}/windows', tags=['Windows'])

# ruff: noqa: FAST003 - параметр пути обрабатывается через зависимость


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
)
async def get_windows(
    project: ProjectVerifiedDep,
    window_service: WindowServiceDep,
    filters: Annotated[WindowFilters, Query()],
) -> PaginatedResponse[WindowPublic]:
    windows = await window_service.get_windows(project.id, filters)

    total = await window_service.count_windows(project.id, filters)

    return PaginatedResponse(
        data=windows,
        total=total,
        page=filters.page,
        limit=filters.limit,
    )


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_window(
    project: ProjectVerifiedDep,
    window_create: WindowCreate,
    window_service: WindowServiceDep,
) -> WindowPublic:
    return await window_service.create_window(project.id, window_create)


@router.get(
    '/{window_id}',
    status_code=status.HTTP_200_OK,
)
async def get_window(
    window: WindowVerifiedDep,
) -> WindowPublic:
    return window


@router.put(
    '/{window_id}',
    status_code=status.HTTP_200_OK,
)
async def update_window(
    window: WindowVerifiedDep,
    window_update: WindowUpdate,
    window_service: WindowServiceDep,
) -> WindowPublic:
    return await window_service.update_window(window.id, window_update)


@router.delete(
    '/{window_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_window(
    window: WindowVerifiedDep,
    window_service: WindowServiceDep,
) -> None:
    await window_service.delete_window(window.id)


@router.post(
    '/{window_id}/{language}',
    status_code=status.HTTP_200_OK,
)
async def generate_code(
    window: WindowVerifiedDep,
    language: TargetLanguage,
    code_generation_service: CodeGenerationServiceDep,
) -> Response:

    result = await code_generation_service.generate(
        window_id=window.id,
        language=language,
    )

    pretty_json = json.dumps(result, indent=4, ensure_ascii=False)

    return Response(
        content=pretty_json,
        media_type='application/json',
    )
