from typing import Optional, Sequence
from uuid import UUID

from app.dependencies.repositories import UserRepository, UserRepositoryDep
from app.models.projects import ProjectModel
from app.models.users import UserCreate, UserModel, UserUpdate
from app.schemas.users import UserFilters
from app.services.hasher import hash_password


class UserService:
    __user_repository: UserRepository

    def __init__(self, user_repository: UserRepositoryDep):
        self.__user_repository = user_repository

    async def get_users(self, filters: UserFilters) -> Sequence[UserModel]:
        return await self.__user_repository.fetch(
            **filters.model_dump(exclude_unset=True)
        )

    async def count_users(self, filters: UserFilters) -> int:
        return await self.__user_repository.count_all(
            **filters.model_dump(exclude_unset=True)
        )

    async def create_user(self, user_create: UserCreate) -> UserModel:
        user_dump = user_create.model_dump()
        password = str(user_dump.pop('password'))
        password_hash = hash_password(password)
        user = UserModel(**user_dump, password_hash=password_hash, is_active=True)
        return await self.__user_repository.save(user)

    async def create_user_model(self, user: UserModel) -> UserModel:
        return await self.__user_repository.save(user)

    async def get_user(self, user_id: UUID) -> Optional[UserModel]:
        return await self.__user_repository.get(user_id)

    async def get_user_by_email(self, email: str) -> Optional[UserModel]:
        users = await self.__user_repository.fetch(email=email)
        if len(users) != 1:
            return None
        return users[0]

    async def update_user(
        self,
        user_update: UserUpdate,
        user_id: UUID,
    ) -> Optional[UserModel]:
        update_data = user_update.model_dump(exclude_unset=True)

        password = update_data.pop('password', None)
        if password is not None:
            update_data['password_hash'] = hash_password(password)

        user_update_with_hash = UserUpdate.model_validate(update_data)
        return await self.__user_repository.update(user_id, user_update_with_hash)

    async def change_password(
        self, user_id: UUID, new_password: str
    ) -> Optional[UserModel]:
        current_user = await self.get_user(user_id)
        if current_user is None:
            return None

        current_user.password_hash = hash_password(new_password)
        return await self.__user_repository.save(current_user)

    async def delete_user(self, user_id: UUID) -> Optional[UserModel]:
        return await self.__user_repository.delete(user_id)

    async def get_user_projects(self, user_id: UUID) -> Sequence[ProjectModel]:
        user = await self.__user_repository.get(user_id)
        if user is None:
            return []
        return user.projects
