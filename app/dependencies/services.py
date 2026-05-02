from typing import Annotated

from fastapi import Depends

from app.dependencies.repositories import (
    ClassRepositoryDep,
    InterfaceRepositoryDep,
    MethodRepositoryDep,
)
from app.services.arguments import ArgumentService
from app.services.attributes import AttributeService
from app.services.classes import ClassService
from app.services.interfaces import InterfaceService
from app.services.methods import MethodService
from app.services.projects import ProjectService
from app.services.rbac import RBACService
from app.services.refresh_session import RefreshSessionService
from app.services.relations import RelationService
from app.services.tiles import TileService
from app.services.users import UserService
from app.services.windows import WindowService

UserServiceDep = Annotated[UserService, Depends(UserService)]

RefreshSessionServiceDep = Annotated[
    RefreshSessionService,
    Depends(RefreshSessionService),
]

RBACServiceDep = Annotated[RBACService, Depends(RBACService)]

ProjectServiceDep = Annotated[ProjectService, Depends(ProjectService)]

WindowServiceDep = Annotated[WindowService, Depends(WindowService)]

TileServiceDep = Annotated[TileService, Depends(TileService)]


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

ArgumentServiceDep = Annotated[ArgumentService, Depends(ArgumentService)]


async def get_method_service(
    method_repository: MethodRepositoryDep,
    argument_service: ArgumentServiceDep,
) -> MethodService:
    return MethodService(method_repository, argument_service)


MethodServiceDep = Annotated[MethodService, Depends(get_method_service)]

AttributeServiceDep = Annotated[AttributeService, Depends(AttributeService)]

RelationServiceDep = Annotated[RelationService, Depends(RelationService)]
