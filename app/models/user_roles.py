from uuid import UUID

from sqlmodel import Field, SQLModel


class UserRoleLink(SQLModel, table=True):
    __tablename__ = 'user_role'

    user_id: UUID = Field(foreign_key='user.id', ondelete='CASCADE', primary_key=True)
    role_id: UUID = Field(foreign_key='role.id', ondelete='CASCADE', primary_key=True)
