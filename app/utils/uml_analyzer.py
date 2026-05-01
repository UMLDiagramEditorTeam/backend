from dataclasses import dataclass
from typing import Iterable

from app.models import ClassModel, InterfaceModel, RelationKind, RelationModel
from app.services.uml_graph_preloader import UMLGraph


@dataclass(slots=True)
class ClassRelations:
    extends: ClassModel | None
    implements: list[InterfaceModel]
    associations: list[ClassModel]


@dataclass(slots=True)
class InterfaceRelations:
    extends: list[InterfaceModel]


class UMLGraphAnalyzer:
    def __init__(self, graph: UMLGraph):
        self._graph = graph

    def analyze_class(
        self,
        class_model: ClassModel,
    ) -> ClassRelations:
        return ClassRelations(
            extends=self.get_parent_class(class_model),
            implements=self.get_implemented_interfaces(class_model),
            associations=self.get_associated_classes(class_model),
        )

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

    def get_implemented_interfaces(
        self,
        class_model: ClassModel,
    ) -> list[InterfaceModel]:
        result: list[InterfaceModel] = []

        for relation in class_model.relations_start:
            if relation.type != RelationKind.REALIZATION:
                continue

            if relation.end_interface_id is None:
                continue

            interface = self._graph.interface_map.get(relation.end_interface_id)

            if interface is not None:
                result.append(interface)

        return result

    def get_associated_classes(
        self,
        class_model: ClassModel,
    ) -> list[ClassModel]:
        result: list[ClassModel] = []

        for relation in class_model.relations_start:
            if relation.type != RelationKind.RELATION:
                continue

            if relation.end_class_id is None:
                continue

            target = self._graph.class_map.get(relation.end_class_id)

            if target is not None:
                result.append(target)

        return result

    def analyze_interface(
        self,
        interface_model: InterfaceModel,
    ) -> InterfaceRelations:
        return InterfaceRelations(
            extends=self.get_parent_interfaces(interface_model),
        )

    def get_parent_interfaces(
        self,
        interface_model: InterfaceModel,
    ) -> list[InterfaceModel]:
        result: list[InterfaceModel] = []

        for relation in interface_model.relation_start:
            if relation.type != RelationKind.REALIZATION:
                continue

            if relation.end_interface_id is None:
                continue

            parent = self._graph.interface_map.get(relation.end_interface_id)

            if parent is not None:
                result.append(parent)

        return result

    def iter_class_relations(
        self,
        class_model: ClassModel,
    ) -> Iterable[RelationModel]:
        return class_model.relations_start

    def iter_interface_relations(
        self,
        interface_model: InterfaceModel,
    ) -> Iterable[RelationModel]:
        return interface_model.relation_start
