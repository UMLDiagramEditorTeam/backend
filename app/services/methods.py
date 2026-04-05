from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import (
    MethodRepository,
    MethodRepositoryDep,
)
from app.models import MethodPublic
from app.models.methods import MethodCreate, MethodModel, MethodUpdate
from app.schemas.methods import MethodFilters
from app.services.arguments import ArgumentService


class MethodService:
    __method_repository: MethodRepository
    __argument_service: ArgumentService

    def __init__(
        self,
        method_repository: MethodRepositoryDep,
        argument_service: ArgumentService,
    ):
        self.__method_repository = method_repository
        self.__argument_service = argument_service

    async def get_methods(
        self,
        filters: MethodFilters,
        class_id: Optional[UUID] = None,
        interface_id: Optional[UUID] = None,
        relations: list[str] | None = None,
    ) -> Sequence[MethodModel]:
        return await self.__method_repository.fetch(
            class_id=class_id,
            interface_id=interface_id,
            relations=relations,
            **filters.model_dump(exclude_unset=True),
        )

    async def count_methods(
        self,
        filters: MethodFilters,
        class_id: Optional[UUID] = None,
        interface_id: Optional[UUID] = None,
    ) -> int:
        return await self.__method_repository.count_all(
            class_id=class_id,
            interface_id=interface_id,
            **filters.model_dump(exclude_unset=True),
        )

    async def get_methods_public(
        self,
        filters: MethodFilters,
        class_id: Optional[UUID] = None,
        interface_id: Optional[UUID] = None,
    ) -> Sequence[MethodPublic]:
        return await self.get_methods(filters, class_id, interface_id, ['arguments'])  # type: ignore[return-value]

    async def get_method(self, method_id: UUID) -> Optional[MethodModel]:
        return await self.__method_repository.get(method_id)

    async def create_method(
        self,
        method_create: MethodCreate,
        class_id: Optional[UUID] = None,
        interface_id: Optional[UUID] = None,
    ) -> MethodModel:
        method_data = method_create.model_dump(exclude={'arguments'})
        method = MethodModel(
            **method_data, class_id=class_id, interface_id=interface_id
        )
        method = await self.__method_repository.save(method)

        arguments = method_create.arguments
        await self.__argument_service.create_arguments(method.id, arguments)

        return method

    async def update_method(
        self,
        method_id: UUID,
        method_update: MethodUpdate,
    ) -> Optional[MethodModel]:
        method = await self.__method_repository.update(method_id, method_update)

        await self.__argument_service.replace_method_arguments(
            method_id, method_update.arguments
        )

        return method

    async def delete_method(self, method_id: UUID) -> Optional[MethodModel]:
        return await self.__method_repository.delete(method_id)
