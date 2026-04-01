from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import RelationRepository, RelationRepositoryDep
from app.models.relations import RelationCreate, RelationModel, RelationUpdate
from app.schemas.relations import RelationFilters


class RelationService:
    __relation_repository: RelationRepository

    def __init__(self, relation_repository: RelationRepositoryDep):
        self.__relation_repository = relation_repository

    async def get_relations(
        self, window_id: UUID, filters: RelationFilters
    ) -> Sequence[RelationModel]:
        return await self.__relation_repository.fetch(
            window_id=window_id, **filters.model_dump(exclude_unset=True)
        )

    async def count_relations(self, window_id: UUID, filters: RelationFilters) -> int:
        return await self.__relation_repository.count_all(
            window_id=window_id, **filters.model_dump(exclude_unset=True)
        )

    async def get_relation(self, relation_id: UUID) -> Optional[RelationModel]:
        return await self.__relation_repository.get(relation_id)

    async def create_relation(
        self, window_id: UUID, relation_create: RelationCreate
    ) -> RelationModel:
        relation = RelationModel(**relation_create.model_dump(), window_id=window_id)

        return await self.__relation_repository.save(relation)

    async def update_relation(
        self, relation_id: UUID, relation_update: RelationUpdate
    ) -> Optional[RelationModel]:
        return await self.__relation_repository.update(relation_id, relation_update)

    async def delete_relation(self, relation_id: UUID) -> Optional[RelationModel]:
        return await self.__relation_repository.delete(relation_id)
