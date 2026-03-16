from datetime import datetime, timezone
from enum import Enum
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy import TIMESTAMP, CheckConstraint
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

sqlite_file_name = 'database.db'

sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {'check_same_thread': False}

engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class BaseModel(SQLModel):
    id: UUID = Field(primary_key=True, default_factory=uuid4)


class AccessModifier(str, Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    PROTECTED = 'protected'


class DiagramType(str, Enum):
    UML = 'uml'
    SEQUENCE = 'sequence'


class RelationType(str, Enum):
    RELATION = 'relation'
    ONE = 'one'
    MANY = 'many'
    ONE_AND_ONLY_ONE = 'one and ONLY one'
    ZERO_OR_ONE = 'zero or one'
    ONE_OR_MANY = 'one or many'
    ZERO_OR_MANY = 'zero or many'


class User(BaseModel, table=True):
    name: str = Field(max_length=100)
    email: str = Field(max_length=100, unique=True)
    password_hash: str = Field(max_length=100)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
    )

    schemes: list['Scheme'] = Relationship(back_populates='user')
    windows: list['Window'] = Relationship(back_populates='user')


class Scheme(BaseModel, table=True):
    is_imported: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
    )
    window_id: UUID | None = Field(default=None, foreign_key='window.id')
    user_id: UUID | None = Field(default=None, foreign_key='user.id')

    window: 'Window' = Relationship(back_populates='schemes')
    user: 'User' = Relationship(back_populates='schemes')


class Window(BaseModel, table=True):
    type: DiagramType = Field(default=DiagramType.UML)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_type=TIMESTAMP(timezone=True),
    )
    user_id: UUID | None = Field(default=None, foreign_key='user.id')

    user: 'User' = Relationship(back_populates='windows')
    schemes: list['Scheme'] = Relationship(back_populates='window')
    tiles: list['Tile'] = Relationship(back_populates='window')


class Tile(BaseModel, table=True):
    is_correct: bool = Field(default=True)
    height: int = Field(default=100, gt=0)
    width: int = Field(default=100, gt=0)
    pos_x: int = Field(default=0, ge=0)
    pos_y: int = Field(default=0, ge=0)
    window_id: UUID | None = Field(default=None, foreign_key='window.id')

    window: 'Window' = Relationship(back_populates='tiles')
    classes: list['Class'] = Relationship(back_populates='tile')
    interfaces: list['Interface'] = Relationship(back_populates='tile')


class Class(BaseModel, table=True):
    access_modifier: AccessModifier = Field(default=AccessModifier.PUBLIC)
    name: str = Field(max_length=100)
    tile_id: UUID | None = Field(default=None, foreign_key='tile.id')

    tile: 'Tile' = Relationship(back_populates='classes')
    attributes: list['Attribute'] = Relationship(back_populates='class')
    methods: list['Method'] = Relationship(back_populates='class')
    relations_start: list['Relation'] = Relationship(back_populates='start_class')
    relations_end: list['Relation'] = Relationship(back_populates='end_class')


class Interface(BaseModel, table=True):
    name: str = Field(max_length=100)
    tile_id: UUID | None = Field(default=None, foreign_key='tile.id')

    tile: 'Tile' = Relationship(back_populates='interfaces')
    methods: list['Method'] = Relationship(back_populates='interface')
    relation_start: list['Relation'] = Relationship(back_populates='start_interface')
    relation_end: list['Relation'] = Relationship(back_populates='end_interface')


class Attribute(BaseModel, table=True):
    name: str = Field(max_length=100)
    access_modifier: AccessModifier = Field(default=AccessModifier.PUBLIC)
    type: str = Field(max_length=100)
    is_final: bool = Field(default=False)
    is_static: bool = Field(default=False)
    class_id: UUID | None = Field(default=None, foreign_key='class.id')

    class_: 'Class' = Relationship(back_populates='attributes')


class Method(BaseModel, table=True):
    name: str = Field(max_length=100)
    access_modifier: AccessModifier = Field(default=AccessModifier.PUBLIC)
    type: str = Field(max_length=100)
    is_final: bool = Field(default=False)
    is_static: bool = Field(default=False)
    class_id: UUID | None = Field(default=None, foreign_key='class.id')
    interface_id: UUID | None = Field(default=None, foreign_key='interface.id')

    class_: 'Class' = Relationship(back_populates='methods')
    interface: 'Interface' = Relationship(back_populates='methods')
    arguments: list['Argument'] = Relationship(back_populates='method')

    __table_args__ = (
        CheckConstraint(
            (
                '(class_id IS NOT NULL AND interface_id IS NULL) '
                'OR (class_id IS NULL AND interface_id IS NOT NULL)'
            ),
            name='single_parent_check',
        ),
    )


class Argument(BaseModel, table=True):
    name: str = Field(max_length=100)
    type: str = Field(max_length=100)
    method_id: UUID | None = Field(default=None, foreign_key='method.id')

    method: 'Method' = Relationship(back_populates='arguments')


class Relation(BaseModel, table=True):
    name: str = Field(max_length=100)
    start_type: RelationType = Field(default=RelationType.RELATION)
    end_type: RelationType = Field(default=RelationType.RELATION)
    start_class_id: UUID | None = Field(default=None, foreign_key='class.id')
    start_interface_id: UUID | None = Field(default=None, foreign_key='interface.id')
    end_class_id: UUID | None = Field(default=None, foreign_key='class.id')
    end_interface_id: UUID | None = Field(default=None, foreign_key='interface.id')

    start_class: 'Class' = Relationship(back_populates='relations_start')
    start_interface: 'Interface' = Relationship(back_populates='relation_start')
    end_class: 'Class' = Relationship(back_populates='relations_end')
    end_interface: 'Interface' = Relationship(back_populates='relation_end')

    __table_args__ = (
        CheckConstraint(
            (
                '(start_class_id IS NOT NULL AND start_interface_id IS NULL) '
                'OR (start_class_id IS NULL AND start_interface_id IS NOT NULL)'
            ),
            name='single_start_entity_check',
        ),
        CheckConstraint(
            (
                '(end_class_id IS NOT NULL AND end_interface_id IS NULL) '
                'OR (end_class_id IS NULL AND end_interface_id IS NOT NULL)'
            ),
            name='single_end_entity_check',
        ),
    )
