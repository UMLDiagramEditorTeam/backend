from dataclasses import dataclass

from app.models import (
    BaseModel,
    ClassModel,
    InterfaceModel,
    MethodModel,
    RelationKind,
)
from app.services.uml_graph_preloader import UMLGraph


@dataclass(slots=True)
class ClassRelations:
    extends: ClassModel | None
    implements: list[InterfaceModel]
    implemented_methods: list[MethodModel]


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

    def get_interface_methods(
        self, implemented: list[InterfaceModel]
    ) -> list[MethodModel]:
        if len(implemented) == 0:
            return []
        return [method for interface in implemented for method in interface.methods]

    def analyze_class(
        self,
        class_model: ClassModel,
    ) -> ClassRelations:
        implements = self.get_parent_interfaces(class_model)
        return ClassRelations(
            extends=self.get_parent_class(class_model),
            implements=implements,
            implemented_methods=self.get_interface_methods(implements),
        )

    def analyze_interface(
        self,
        interface_model: InterfaceModel,
    ) -> InterfaceRelations:
        return InterfaceRelations(
            extends=self.get_parent_interfaces(interface_model),
        )
