# app/dependencies/services.py
from typing import Annotated

from fastapi import Depends

from app.dependencies.repositories import (
    ArgumentRepositoryDep,
    AttributeRepositoryDep,
    ClassRepositoryDep,
    InterfaceRepositoryDep,
    MethodRepositoryDep,
    ProjectRepositoryDep,
    RelationRepositoryDep,
    TileRepositoryDep,
    UserRepositoryDep,
    WindowRepositoryDep,
)
from app.services.arguments import ArgumentService
from app.services.attributes import AttributeService
from app.services.classes import ClassService
from app.services.interfaces import InterfaceService
from app.services.methods import MethodService
from app.services.projects import ProjectService
from app.services.relations import RelationService
from app.services.tiles import TileService
from app.services.users import UserService
from app.services.windows import WindowService


async def get_user_service(user_repository: UserRepositoryDep) -> UserService:
    return UserService(user_repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_project_service(
    project_repository: ProjectRepositoryDep,
) -> ProjectService:
    return ProjectService(project_repository)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]


async def get_window_service(
    window_repository: WindowRepositoryDep,
) -> WindowService:
    return WindowService(window_repository)


WindowServiceDep = Annotated[WindowService, Depends(get_window_service)]


async def get_tile_service(
    tile_repository: TileRepositoryDep,
) -> TileService:
    return TileService(tile_repository)


TileServiceDep = Annotated[TileService, Depends(get_tile_service)]


async def get_class_service(
    class_repository: ClassRepositoryDep,
    tile_service: TileServiceDep,
) -> ClassService:
    return ClassService(class_repository, tile_service)


ClassServiceDep = Annotated[ClassService, Depends(get_class_service)]


async def get_interface_srvice(
    interface_repository: InterfaceRepositoryDep,
    tile_service: TileServiceDep,
) -> InterfaceService:
    return InterfaceService(interface_repository, tile_service)


InterfaceServiceDep = Annotated[InterfaceService, Depends(get_interface_srvice)]


async def get_arguments_service(
    arguments_repository: ArgumentRepositoryDep,
) -> ArgumentService:
    return ArgumentService(arguments_repository)


ArgumentServiceDep = Annotated[ArgumentService, Depends(get_arguments_service)]


async def get_method_service(
    method_repository: MethodRepositoryDep,
    argument_service: ArgumentServiceDep,
) -> MethodService:
    return MethodService(method_repository, argument_service)


MethodServiceDep = Annotated[MethodService, Depends(get_method_service)]


async def get_attribute_service(
    attribute_repository: AttributeRepositoryDep,
) -> AttributeService:
    return AttributeService(attribute_repository)


AttributeServiceDep = Annotated[AttributeService, Depends(get_attribute_service)]


async def get_relation_service(
    relation_repository: RelationRepositoryDep,
) -> RelationService:
    return RelationService(relation_repository)


RelationServiceDep = Annotated[RelationService, Depends(get_relation_service)]
