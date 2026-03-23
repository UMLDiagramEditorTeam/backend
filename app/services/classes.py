from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import (
    ClassRepository,
    ClassRepositoryDep,
)
from app.models.classes import ClassCreate, ClassModel, ClassPublic, ClassUpdate
from app.schemas.classes import ClassFilters
from app.services.tiles import TileService


class ClassService:
    __class_repository: ClassRepository
    __tile_service: TileService

    def __init__(
        self,
        class_repository: ClassRepositoryDep,
        tile_service: TileService,
    ):
        self.__class_repository = class_repository
        self.__tile_service = tile_service

    async def get_classes(
        self, window_id: UUID, filters: ClassFilters, relations: list[str] | None = None
    ) -> Sequence[ClassModel]:
        return await self.__class_repository.fetch(
            window_id=window_id,
            relations=relations,
            **filters.model_dump(exclude_unset=True),
        )

    async def get_classes_public(
        self, window_id: UUID, filters: ClassFilters
    ) -> Sequence[ClassPublic]:
        classes = await self.get_classes(window_id, filters, ['tile'])
        return list(map(ClassPublic.from_model, classes))

    async def count_classes(self, window_id: UUID, filters: ClassFilters) -> int:
        return await self.__class_repository.count_all(
            window_id=window_id, **filters.model_dump(exclude_unset=True)
        )

    async def get_class(self, class_id: UUID) -> Optional[ClassModel]:
        return await self.__class_repository.get(class_id)

    async def create_class(
        self, class_create: ClassCreate, window_id: UUID
    ) -> ClassModel:
        tile = await self.__tile_service.create_tile(class_create.tile)

        class_model = ClassModel(
            **class_create.model_dump(exclude={'tile'}),
            window_id=window_id,
            tile_id=tile.id,
        )

        return await self.__class_repository.save(class_model)

    async def update_class(
        self, class_id: UUID, class_update: ClassUpdate
    ) -> Optional[ClassModel]:
        class_ = await self.__class_repository.get(class_id)
        await self.__tile_service.update_tile(class_.tile_id, class_update.tile)
        return await self.__class_repository.update(class_id, class_update)

    async def delete_class(self, class_id: UUID) -> Optional[ClassModel]:
        return await self.__class_repository.delete(class_id)
