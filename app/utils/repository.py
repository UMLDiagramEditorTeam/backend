from typing import Optional, Sequence
from uuid import UUID

from generics import get_filled_type
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import and_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.dependencies.session import SessionDep
from app.models import BaseModel


class Repository[Model: BaseModel]:
    __model: type[Model] | None = None
    __session: AsyncSession

    @property
    def model(self) -> type[Model]:
        if self.__model is None:
            self.__model = get_filled_type(self, Repository, 0)
        return self.__model

    def __init__(self, session: SessionDep):
        self.__session = session

    async def get(self, pk: UUID) -> Optional[Model]:
        return await self.__session.get(self.model, pk)

    def prepare_statement(self, statement, **filters):
        if filters is not None:
            filter_statement = and_(True)
            for key, value in filters.items():
                if not hasattr(self.model, key):
                    continue
                if value is not None:
                    filter_statement = and_(
                        filter_statement, getattr(self.model, key) == value
                    )
            statement = statement.where(filter_statement)
        return statement

    async def fetch(
        self, relations: list[str] | None = None, **filters
    ) -> Sequence[Model]:
        select_statement = select(self.model)
        select_statement = self.prepare_statement(select_statement, **filters)

        if relations is not None:
            for relation in relations:
                select_statement = select_statement.options(
                    selectinload(getattr(self.model, relation))
                )

        if filters.get('offset') is not None:
            select_statement = select_statement.offset(filters['offset'])
        if filters.get('limit') is not None:
            select_statement = select_statement.limit(filters['limit'])
        entities = await self.__session.exec(select_statement)
        return entities.all()

    async def count_all(self, **filters) -> int:
        count_statement = select(func.count()).select_from(self.model)
        count_statement = self.prepare_statement(count_statement, **filters)
        result = await self.__session.exec(count_statement)
        return result.one()

    async def save(self, instance: Model) -> Model:
        self.__session.add(instance)
        await self.__session.commit()
        await self.__session.refresh(instance)
        return instance

    async def save_all(self, instances: list[Model]) -> list[Model]:
        self.__session.add_all(instances)
        await self.__session.commit()
        for instance in instances:
            await self.__session.refresh(instance)
        return instances

    async def delete(self, pk: UUID) -> Optional[Model]:
        instance = await self.get(pk)
        if instance is None:
            return instance
        await self.__session.delete(instance)
        await self.__session.commit()
        return instance

    async def update(self, pk: UUID, updates: PydanticBaseModel) -> Optional[Model]:
        instance = await self.get(pk)
        if instance is None:
            return None
        instance_update_dump = updates.model_dump(exclude_unset=True)
        for key, value in instance_update_dump.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.save(instance)
        return instance
