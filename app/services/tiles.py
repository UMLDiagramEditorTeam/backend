from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import TileRepository, TileRepositoryDep
from app.models.tiles import TileCreate, TileModel, TileUpdate
from app.schemas.tiles import TileFilters


class TileService:
    __tile_repository: TileRepository

    def __init__(self, tile_repository: TileRepositoryDep):
        self.__tile_repository = tile_repository

    async def get_tiles(self, filters: TileFilters) -> Sequence[TileModel]:
        return await self.__tile_repository.fetch(
            **filters.model_dump(exclude_unset=True)
        )

    async def get_tile(self, tile_id: UUID) -> Optional[TileModel]:
        return await self.__tile_repository.get(tile_id)

    async def create_tile(self, tile_create: TileCreate) -> TileModel:
        tile = TileModel(
            **tile_create.model_dump(),
        )
        return await self.__tile_repository.save(tile)

    async def update_tile(
        self, tile_id: UUID, tile_update: TileUpdate
    ) -> Optional[TileModel]:
        return await self.__tile_repository.update(tile_id, tile_update)

    async def delete_tile(self, tile_id: UUID) -> Optional[TileModel]:
        return await self.__tile_repository.delete(tile_id)
