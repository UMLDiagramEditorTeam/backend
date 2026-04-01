from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import (
    InterfaceRepository,
    InterfaceRepositoryDep,
)
from app.models.interfaces import (
    InterfaceCreate,
    InterfaceModel,
    InterfacePublic,
    InterfaceUpdate,
)
from app.schemas.interfaces import InterfaceFilters
from app.services.tiles import TileService


class InterfaceService:
    __interface_repository: InterfaceRepository
    __tile_service: TileService

    def __init__(
        self,
        interface_repository: InterfaceRepositoryDep,
        tile_service: TileService,
    ):
        self.__interface_repository = interface_repository
        self.__tile_service = tile_service

    async def get_interfaces(
        self,
        window_id: UUID,
        filters: InterfaceFilters,
        relations: list[str] | None = None,
    ) -> Sequence[InterfaceModel]:
        return await self.__interface_repository.fetch(
            window_id=window_id,
            **filters.model_dump(exclude_unset=True),
            relations=relations,
        )

    async def get_interfaces_public(
        self, window_id: UUID, filters: InterfaceFilters
    ) -> Sequence[InterfacePublic]:
        interfaces = await self.get_interfaces(window_id, filters, ['tile'])
        return list(map(InterfacePublic.from_model, interfaces))

    async def count_interfaces(self, window_id: UUID, filters: InterfaceFilters) -> int:
        return await self.__interface_repository.count_all(
            window_id=window_id, **filters.model_dump(exclude_unset=True)
        )

    async def get_interface(self, interface_id: UUID) -> Optional[InterfaceModel]:
        return await self.__interface_repository.get(interface_id)

    async def create_interface(
        self, window_id: UUID, interface_create: InterfaceCreate
    ) -> InterfaceModel:
        tile = await self.__tile_service.create_tile(interface_create.tile)

        interface = InterfaceModel(
            **interface_create.model_dump(exclude={'tile'}),
            tile_id=tile.id,
            window_id=window_id,
        )
        return await self.__interface_repository.save(interface)

    async def update_interface(
        self, interface_id: UUID, interface_update: InterfaceUpdate
    ) -> Optional[InterfaceModel]:
        interface = await self.__interface_repository.get(interface_id)
        await self.__tile_service.update_tile(interface.tile_id, interface_update.tile)
        return await self.__interface_repository.update(interface_id, interface_update)

    async def delete_interface(self, interface_id: UUID) -> Optional[InterfaceModel]:
        return await self.__interface_repository.delete(interface_id)
