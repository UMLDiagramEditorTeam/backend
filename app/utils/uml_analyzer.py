from dataclasses import dataclass

from app.models import (
    BaseModel,
    ClassModel,
    InterfaceModel,
    RelationKind,
)
from app.services.uml_graph_preloader import UMLGraph


@dataclass(slots=True)
class ClassRelations:
    extends: ClassModel | None
    implements: list[InterfaceModel]


@dataclass(slots=True)
class InterfaceRelations:
    extends: list[InterfaceModel]


class UMLGraphAnalyzer:
    def __init__(self, graph: UMLGraph):
        self._graph = graph

    def get_parent_class(
        self,
        class_model: ClassModel,
    ) -> ClassModel | None:
        for relation in class_model.relations_start:
            if relation.type != RelationKind.REALIZATION:
                continue

            if relation.end_class_id is None:
                continue

            parent = self._graph.class_map.get(relation.end_class_id)

            if parent is not None:
                return parent

        return None

    def get_parent_interfaces(
        self,
        model: BaseModel,
    ) -> list[InterfaceModel]:
        result: list[InterfaceModel] = []

        for relation in model.relations_start:
            if relation.type != RelationKind.REALIZATION:
                continue

            if relation.end_interface_id is None:
                continue

            parent = self._graph.interface_map.get(relation.end_interface_id)

            if parent is not None:
                result.append(parent)

        return result

    def analyze_class(
        self,
        class_model: ClassModel,
    ) -> ClassRelations:
        return ClassRelations(
            extends=self.get_parent_class(class_model),
            implements=self.get_parent_interfaces(class_model),
        )

    def analyze_interface(
        self,
        interface_model: InterfaceModel,
    ) -> InterfaceRelations:
        return InterfaceRelations(
            extends=self.get_parent_interfaces(interface_model),
        )
