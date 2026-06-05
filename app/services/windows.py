from typing import Optional, Sequence
from uuid import UUID

from app.core.errors import ConflictError
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

    async def _assert_name_unique(
        self, project_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> None:
        existing = await self.__window_repository.fetch(
            project_id=project_id, name=name
        )
        for item in existing:
            if exclude_id is None or item.id != exclude_id:
                raise ConflictError(
                    'Окно с таким названием уже существует в данном проекте'
                )

    async def create_window(
        self, project_id: UUID, window_create: WindowCreate
    ) -> WindowModel:
        await self._assert_name_unique(project_id, window_create.name)

        window = WindowModel(**window_create.model_dump(), project_id=project_id)
        return await self.__window_repository.save(window)

    async def update_window(
        self, window_id: UUID, window_update: WindowUpdate
    ) -> Optional[WindowModel]:
        window = await self.__window_repository.get(window_id)
        if window is None:
            return None

        await self._assert_name_unique(
            window.project_id, window_update.name, exclude_id=window_id
        )

        return await self.__window_repository.update(window_id, window_update)

    async def delete_window(self, window_id: UUID) -> Optional[WindowModel]:
        return await self.__window_repository.delete(window_id)
