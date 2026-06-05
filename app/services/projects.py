from typing import Optional, Sequence
from uuid import UUID

from app.core.errors import ConflictError
from app.dependencies.repositories import ProjectRepository, ProjectRepositoryDep
from app.models.projects import ProjectCreate, ProjectModel, ProjectUpdate
from app.schemas.projects import ProjectFilters


class ProjectService:
    __project_repository: ProjectRepository

    def __init__(self, project_repository: ProjectRepositoryDep):
        self.__project_repository = project_repository

    async def get_projects(
        self, filters: ProjectFilters, user_id: Optional[UUID] = None
    ) -> Sequence[ProjectModel]:
        filters_dict = filters.model_dump(exclude_unset=True)
        if user_id is not None:
            filters_dict['user_id'] = user_id
        return await self.__project_repository.fetch(**filters_dict)

    async def count_projects(
        self, filters: ProjectFilters, user_id: UUID | None = None
    ) -> int:
        filters_dict = filters.model_dump(exclude_unset=True)
        if user_id is not None:
            filters_dict['user_id'] = user_id
        return await self.__project_repository.count_all(**filters_dict)

    async def get_project(self, project_id: UUID) -> Optional[ProjectModel]:
        return await self.__project_repository.get(project_id)

    async def check_ownership(self, project_id: UUID, user_id: UUID) -> bool:
        project = await self.__project_repository.get(project_id)
        if project is None:
            return False
        return project.user_id == user_id

    async def _assert_name_unique(
        self, user_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> None:
        existing = await self.__project_repository.fetch(user_id=user_id, name=name)
        for item in existing:
            if exclude_id is None or item.id != exclude_id:
                raise ConflictError('У вас уже есть проект с таким названием')

    async def create_project(
        self, project_create: ProjectCreate, user_id: UUID
    ) -> ProjectModel:
        await self._assert_name_unique(user_id, project_create.name)

        project = ProjectModel(
            **project_create.model_dump(),
            user_id=user_id,
        )
        return await self.__project_repository.save(project)

    async def update_project(
        self, project_id: UUID, project_update: ProjectUpdate
    ) -> Optional[ProjectModel]:
        project = await self.__project_repository.get(project_id)
        if project is None:
            return None

        await self._assert_name_unique(
            project.user_id, project_update.name, exclude_id=project_id
        )

        return await self.__project_repository.update(project_id, project_update)

    async def delete_project(self, project_id: UUID) -> Optional[ProjectModel]:
        return await self.__project_repository.delete(project_id)
