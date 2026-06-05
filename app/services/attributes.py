from typing import Optional, Sequence
from uuid import UUID

from app.core.errors import ConflictError
from app.dependencies.repositories import AttributeRepository, AttributeRepositoryDep
from app.models.attributes import AttributeCreate, AttributeModel, AttributeUpdate
from app.schemas.attributes import AttributeFilters


class AttributeService:
    __attribute_repository: AttributeRepository

    def __init__(self, attribute_repository: AttributeRepositoryDep):
        self.__attribute_repository = attribute_repository

    async def get_attributes(
        self, class_id: UUID, filters: AttributeFilters
    ) -> Sequence[AttributeModel]:
        return await self.__attribute_repository.fetch(
            class_id=class_id, **filters.model_dump(exclude_unset=True)
        )

    async def count_attributes(self, class_id: UUID, filters: AttributeFilters) -> int:
        return await self.__attribute_repository.count_all(
            class_id=class_id, **filters.model_dump(exclude_unset=True)
        )

    async def get_attribute(self, attribute_id: UUID) -> Optional[AttributeModel]:
        return await self.__attribute_repository.get(attribute_id)

    async def _assert_name_unique(
        self, class_id: UUID, name: str, exclude_id: UUID | None = None
    ) -> None:
        existing = await self.__attribute_repository.fetch(class_id=class_id, name=name)
        for item in existing:
            if exclude_id is None or item.id != exclude_id:
                raise ConflictError(
                    'Аттрибут с таким именем уже существует у данного класса'
                )

    async def create_attribute(
        self,
        attribute_create: AttributeCreate,
        class_id: UUID,
    ) -> AttributeModel:
        await self._assert_name_unique(class_id, attribute_create.name)

        attribute = AttributeModel(
            **attribute_create.model_dump(),
            class_id=class_id,
        )
        return await self.__attribute_repository.save(attribute)

    async def update_attribute(
        self, attribute_id: UUID, attribute_update: AttributeUpdate
    ) -> Optional[AttributeModel]:
        attribute = await self.__attribute_repository.get(attribute_id)
        if attribute is None:
            return None

        await self._assert_name_unique(
            attribute.class_id, attribute_update.name, exclude_id=attribute_id
        )

        return await self.__attribute_repository.update(attribute_id, attribute_update)

    async def delete_attribute(self, attribute_id: UUID) -> Optional[AttributeModel]:
        return await self.__attribute_repository.delete(attribute_id)
