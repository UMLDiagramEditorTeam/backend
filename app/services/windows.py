from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import WindowRepository, WindowRepositoryDep
from app.models.windows import WindowCreate, WindowModel, WindowUpdate
from app.schemas.windows import WindowFilters


class WindowService:
    __window_repository: WindowRepository

    def __init__(self, window_repository: WindowRepositoryDep):
        self.__window_repository = window_repository

    async def get_windows(
        self, project_id: UUID, filters: WindowFilters
    ) -> Sequence[WindowModel]:
        return await self.__window_repository.fetch(
            project_id=project_id, **filters.model_dump(exclude_unset=True)
        )

    async def count_windows(self, project_id: UUID, filters: WindowFilters) -> int:
        return await self.__window_repository.count_all(
            project_id=project_id, **filters.model_dump(exclude_unset=True)
        )

    async def get_window(self, window_id: UUID) -> Optional[WindowModel]:
        return await self.__window_repository.get(window_id)

    async def create_window(
        self, project_id: UUID, window_create: WindowCreate
    ) -> WindowModel:
        window = WindowModel(**window_create.model_dump(), project_id=project_id)
        return await self.__window_repository.save(window)

    async def update_window(
        self, window_id: UUID, window_update: WindowUpdate
    ) -> Optional[WindowModel]:
        return await self.__window_repository.update(window_id, window_update)

    async def delete_window(self, window_id: UUID) -> Optional[WindowModel]:
        return await self.__window_repository.delete(window_id)
