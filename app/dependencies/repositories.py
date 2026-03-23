from typing import Annotated

from fastapi import Depends

from app.dependencies.session import SessionDep
from app.models import UserModel
from app.models.arguments import ArgumentModel
from app.models.attributes import AttributeModel
from app.models.classes import ClassModel
from app.models.interfaces import InterfaceModel
from app.models.methods import MethodModel
from app.models.projects import ProjectModel
from app.models.relations import RelationModel
from app.models.tiles import TileModel
from app.models.windows import WindowModel
from app.utils.repository import Repository


async def get_user_repository(session: SessionDep):
    yield Repository[UserModel](session)


type UserRepository = Repository[UserModel]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


async def get_project_repository(session: SessionDep):
    yield Repository[ProjectModel](session)


type ProjectRepository = Repository[ProjectModel]
ProjectRepositoryDep = Annotated[ProjectRepository, Depends(get_project_repository)]


async def get_window_repository(session: SessionDep):
    yield Repository[WindowModel](session)


type WindowRepository = Repository[WindowModel]
WindowRepositoryDep = Annotated[WindowRepository, Depends(get_window_repository)]


async def get_tile_repository(session: SessionDep):
    yield Repository[TileModel](session)


type TileRepository = Repository[TileModel]
TileRepositoryDep = Annotated[TileRepository, Depends(get_tile_repository)]


async def get_class_repository(session: SessionDep):
    yield Repository[ClassModel](session)


type ClassRepository = Repository[ClassModel]
ClassRepositoryDep = Annotated[ClassRepository, Depends(get_class_repository)]


async def get_interface_repository(session: SessionDep):
    yield Repository[InterfaceModel](session)


type InterfaceRepository = Repository[InterfaceModel]
InterfaceRepositoryDep = Annotated[
    InterfaceRepository, Depends(get_interface_repository)
]


async def get_attribute_repository(session: SessionDep):
    yield Repository[AttributeModel](session)


type AttributeRepository = Repository[AttributeModel]
AttributeRepositoryDep = Annotated[
    AttributeRepository, Depends(get_attribute_repository)
]


async def get_method_repository(session: SessionDep):
    yield Repository[MethodModel](session)


type MethodRepository = Repository[MethodModel]
MethodRepositoryDep = Annotated[MethodRepository, Depends(get_method_repository)]


async def get_argument_repository(session: SessionDep):
    yield Repository[ArgumentModel](session)


type ArgumentRepository = Repository[ArgumentModel]
ArgumentRepositoryDep = Annotated[ArgumentRepository, Depends(get_argument_repository)]


async def get_relation_repository(session: SessionDep):
    yield Repository[RelationModel](session)


type RelationRepository = Repository[RelationModel]
RelationRepositoryDep = Annotated[RelationRepository, Depends(get_relation_repository)]
