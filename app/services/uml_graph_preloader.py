from dataclasses import dataclass
from uuid import UUID

from app.dependencies.services import (
    ClassServiceDep,
    InterfaceServiceDep,
    RelationServiceDep,
    WindowServiceDep,
)
from app.models import ClassModel, InterfaceModel, RelationModel, WindowModel
from app.schemas import ClassFilters, InterfaceFilters, RelationFilters
from app.services.classes import ClassService
from app.services.interfaces import InterfaceService
from app.services.relations import RelationService
from app.services.windows import WindowService


@dataclass(slots=True)
class UMLGraph:
    window: WindowModel

    classes: list[ClassModel]
    interfaces: list[InterfaceModel]
    relations: list[RelationModel]

    class_map: dict[UUID, ClassModel]
    interface_map: dict[UUID, InterfaceModel]


class UMLGraphPreloaderService:
    __window_service: WindowService
    __class_service: ClassService
    __interface_service: InterfaceService
    __relation_service: RelationService

    def __init__(
        self,
        window_service: WindowServiceDep,
        class_service: ClassServiceDep,
        interface_service: InterfaceServiceDep,
        relation_service: RelationServiceDep,
    ):
        self.__window_service = window_service
        self.__class_service = class_service
        self.__interface_service = interface_service
        self.__relation_service = relation_service

    async def load_window_graph(
        self,
        window_id: UUID,
    ) -> UMLGraph:

        window = await self.__window_service.get_window(window_id)

        if window is None:
            raise ValueError(f'Window {window_id} not found')

        classes = list(
            await self.__class_service.get_classes(
                window_id=window_id,
                filters=ClassFilters(),
                relations=[
                    'attributes',
                    'methods',
                    'methods.arguments',
                    'relations_start',
                    'relations_end',
                ],
            )
        )

        interfaces = list(
            await self.__interface_service.get_interfaces(
                window_id=window_id,
                filters=InterfaceFilters(),
                relations=[
                    'methods',
                    'methods.arguments',
                    'relation_start',
                    'relation_end',
                ],
            )
        )

        relations = list(
            await self.__relation_service.get_relations(
                window_id=window_id,
                filters=RelationFilters(),
            )
        )

        class_map = {class_model.id: class_model for class_model in classes}

        interface_map = {interface.id: interface for interface in interfaces}

        return UMLGraph(
            window=window,
            classes=classes,
            interfaces=interfaces,
            relations=relations,
            class_map=class_map,
            interface_map=interface_map,
        )
