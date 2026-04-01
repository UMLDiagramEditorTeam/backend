from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import ArgumentRepository, ArgumentRepositoryDep
from app.models.arguments import ArgumentCreate, ArgumentModel


class ArgumentService:
    __argument_repository: ArgumentRepository

    def __init__(self, argument_repository: ArgumentRepositoryDep):
        self.__argument_repository = argument_repository

    async def get_arguments(self, method_id: UUID) -> Sequence[ArgumentModel]:
        return await self.__argument_repository.fetch(method_id=method_id)

    async def get_argument(self, argument_id: UUID) -> Optional[ArgumentModel]:
        return await self.__argument_repository.get(argument_id)

    async def create_argument(
        self,
        argument_create: ArgumentCreate,
        method_id: UUID,
    ) -> ArgumentModel:
        argument = ArgumentModel(
            **argument_create.model_dump(),
            method_id=method_id,
        )
        return await self.__argument_repository.save(argument)

    async def create_arguments(
        self, method_id: UUID, arguments_create: list[ArgumentCreate]
    ) -> list[ArgumentModel]:
        arguments = [
            ArgumentModel(**arg.model_dump(), method_id=method_id)
            for arg in arguments_create
        ]
        return await self.__argument_repository.save_all(arguments)

    async def update_argument(
        self, argument_id: UUID, argument_update: ArgumentCreate
    ) -> Optional[ArgumentModel]:
        return await self.__argument_repository.update(argument_id, argument_update)

    async def delete_argument(self, argument_id: UUID) -> Optional[ArgumentModel]:
        return await self.__argument_repository.delete(argument_id)

    async def delete_arguments_by_method(self, method_id: UUID) -> None:
        arguments = await self.get_arguments(method_id)
        for argument in arguments:
            await self.__argument_repository.delete(argument.id)

    async def get_method_arguments(self, method_id: UUID) -> Sequence[ArgumentModel]:
        return await self.__argument_repository.fetch(method_id=method_id)

    async def replace_method_arguments(
        self,
        method_id: UUID,
        new_arguments: list[ArgumentCreate],
    ) -> list[ArgumentModel]:
        await self.delete_arguments_by_method(method_id)

        return await self.create_arguments(method_id, new_arguments)
