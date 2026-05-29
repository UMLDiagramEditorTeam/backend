from collections import Counter, defaultdict
from uuid import UUID

from app.models import MethodModel, RelationKind, RelationModel
from app.services.uml_graph_preloader import UMLGraph
from app.utils.generator_factory import TargetLanguage

NodeKey = tuple[str, UUID]


class CodeGenerationValidator:
    def validate(self, graph: UMLGraph, language: TargetLanguage) -> list[str]:
        errors = self._validate_common(graph)

        if language == TargetLanguage.JAVA:
            errors.extend(self._validate_java(graph))
        elif language == TargetLanguage.PYTHON:
            errors.extend(self._validate_python(graph))

        return errors

    def _validate_common(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        errors.extend(self._validate_names(graph))
        errors.extend(self._validate_generated_file_names(graph))
        errors.extend(self._validate_methods(graph))
        errors.extend(self._validate_relations(graph))
        errors.extend(self._validate_realization_cycles(graph))

        return errors

    def _validate_java(self, _graph: UMLGraph) -> list[str]:
        return []

    def _validate_python(self, _graph: UMLGraph) -> list[str]:
        return []

    def _validate_names(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for class_model in graph.classes:
            if self._is_blank(class_model.name):
                errors.append(f'Class {class_model.id} has empty name')

        for interface in graph.interfaces:
            if self._is_blank(interface.name):
                errors.append(f'Interface {interface.id} has empty name')

        return errors

    def _validate_generated_file_names(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []
        names: defaultdict[str, list[str]] = defaultdict(list)

        for class_model in graph.classes:
            if not self._is_blank(class_model.name):
                names[class_model.name].append(f'class {class_model.name}')

        for interface in graph.interfaces:
            if not self._is_blank(interface.name):
                names[interface.name].append(f'interface {interface.name}')

        for name, owners in names.items():
            if len(owners) > 1:
                errors.append(
                    f'Generated file name conflict for {name}: {", ".join(owners)}'
                )

        return errors

    def _validate_methods(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for class_model in graph.classes:
            errors.extend(
                self._validate_owner_methods(
                    owner_name=f'class {class_model.name}',
                    methods=class_model.methods,
                )
            )

        for interface in graph.interfaces:
            errors.extend(
                self._validate_owner_methods(
                    owner_name=f'interface {interface.name}',
                    methods=interface.methods,
                )
            )

        return errors

    def _validate_owner_methods(
        self,
        *,
        owner_name: str,
        methods: list[MethodModel],
    ) -> list[str]:
        errors: list[str] = []
        signatures: Counter[str] = Counter()

        for method in methods:
            if self._is_blank(method.name):
                errors.append(f'Method {method.id} in {owner_name} has empty name')

            if self._is_blank(method.return_type):
                errors.append(
                    f'Method {method.name} in {owner_name} has empty return type'
                )

            errors.extend(self._validate_arguments(owner_name, method))
            signatures[self._method_signature(method)] += 1

        for signature, count in signatures.items():
            if count > 1:
                errors.append(f'Duplicate method signature {signature} in {owner_name}')

        return errors

    def _validate_arguments(self, owner_name: str, method: MethodModel) -> list[str]:
        errors: list[str] = []
        names: Counter[str] = Counter()
        order_numbers: Counter[int] = Counter()

        for argument in method.arguments:
            if self._is_blank(argument.name):
                errors.append(
                    f'Argument {argument.id} in method {method.name} of {owner_name} '
                    'has empty name'
                )
            else:
                names[argument.name] += 1

            if self._is_blank(argument.type):
                errors.append(
                    f'Argument {argument.name} in method {method.name} of '
                    f'{owner_name} has empty type'
                )

            order_numbers[argument.order_num] += 1

        for name, count in names.items():
            if count > 1:
                errors.append(
                    f'Duplicate argument name {name} in method {method.name} of '
                    f'{owner_name}'
                )

        for order_num, count in order_numbers.items():
            if count > 1:
                errors.append(
                    f'Duplicate argument order {order_num} in method {method.name} '
                    f'of {owner_name}'
                )

        return errors

    def _validate_relations(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for relation in graph.relations:
            begin = self._relation_begin(relation)
            end = self._relation_end(relation)

            if begin is None:
                errors.append(f'Relation {relation.name} has invalid begin endpoint')
            elif not self._node_exists(begin, graph):
                errors.append(
                    f'Relation {relation.name} references missing begin endpoint'
                )

            if end is None:
                errors.append(f'Relation {relation.name} has invalid end endpoint')
            elif not self._node_exists(end, graph):
                errors.append(
                    f'Relation {relation.name} references missing end endpoint'
                )

            if (
                relation.type == RelationKind.REALIZATION
                and begin is not None
                and end is not None
                and begin == end
            ):
                errors.append(
                    f'Relation {relation.name} cannot point to the same entity'
                )

        return errors

    def _validate_realization_cycles(self, graph: UMLGraph) -> list[str]:
        graph_edges: defaultdict[NodeKey, list[NodeKey]] = defaultdict(list)

        for relation in graph.relations:
            if relation.type != RelationKind.REALIZATION:
                continue

            begin = self._relation_begin(relation)
            end = self._relation_end(relation)

            if begin is None or end is None:
                continue

            if not self._node_exists(begin, graph) or not self._node_exists(end, graph):
                continue

            graph_edges[begin].append(end)

        return self._find_cycles(graph_edges, graph)

    def _find_cycles(
        self,
        graph_edges: dict[NodeKey, list[NodeKey]],
        graph: UMLGraph,
    ) -> list[str]:
        errors: list[str] = []
        visiting: set[NodeKey] = set()
        visited: set[NodeKey] = set()
        stack: list[NodeKey] = []

        def visit(node: NodeKey) -> None:
            if node in visited:
                return

            if node in visiting:
                cycle = stack[stack.index(node) :] + [node]
                names = ' -> '.join(self._node_name(item, graph) for item in cycle)
                errors.append(f'Cyclic realization detected: {names}')
                return

            visiting.add(node)
            stack.append(node)

            for next_node in graph_edges.get(node, []):
                visit(next_node)

            stack.pop()
            visiting.remove(node)
            visited.add(node)

        for node in graph_edges:
            visit(node)

        return errors

    def _relation_begin(self, relation: RelationModel) -> NodeKey | None:
        return self._relation_endpoint(
            class_id=relation.begin_class_id,
            interface_id=relation.begin_interface_id,
        )

    def _relation_end(self, relation: RelationModel) -> NodeKey | None:
        return self._relation_endpoint(
            class_id=relation.end_class_id,
            interface_id=relation.end_interface_id,
        )

    def _relation_endpoint(
        self,
        *,
        class_id: UUID | None,
        interface_id: UUID | None,
    ) -> NodeKey | None:
        endpoint_count = sum(item is not None for item in (class_id, interface_id))

        if endpoint_count != 1:
            return None

        if class_id is not None:
            return ('class', class_id)

        if interface_id is not None:
            return ('interface', interface_id)

        return None

    def _node_exists(self, node: NodeKey, graph: UMLGraph) -> bool:
        node_type, node_id = node

        if node_type == 'class':
            return node_id in graph.class_map

        if node_type == 'interface':
            return node_id in graph.interface_map

        return False

    def _node_name(self, node: NodeKey, graph: UMLGraph) -> str:
        node_type, node_id = node

        if node_type == 'class':
            class_model = graph.class_map.get(node_id)
            return class_model.name if class_model is not None else str(node_id)

        interface = graph.interface_map.get(node_id)
        return interface.name if interface is not None else str(node_id)

    def _method_signature(self, method: MethodModel) -> str:
        arguments = sorted(method.arguments, key=lambda argument: argument.order_num)
        argument_types = ','.join(argument.type for argument in arguments)
        return f'{method.name}({argument_types})'

    def _is_blank(self, value: str | None) -> bool:
        return value is None or value.strip() == ''
