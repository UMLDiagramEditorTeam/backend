import keyword
from collections import Counter, defaultdict
from uuid import UUID

from app.models import (
    AccessModifier,
    ClassModel,
    InterfaceModel,
    MethodModel,
    RelationKind,
    RelationModel,
)
from app.services.uml_graph_preloader import UMLGraph
from app.utils.generator_factory import TargetLanguage
from app.utils.uml_analyzer import UMLGraphAnalyzer

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

    def _validate_java(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        errors.extend(self._validate_java_classes(graph))
        errors.extend(self._validate_java_interface_methods(graph))
        errors.extend(self._validate_java_interface_implementations(graph))

        return errors

    def _validate_python(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        errors.extend(self._validate_python_identifiers(graph))
        errors.extend(self._validate_python_method_names(graph))
        errors.extend(self._validate_python_parents(graph))

        return errors

    def _validate_python_identifiers(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for class_model in graph.classes:
            if not self._is_python_identifier(class_model.name):
                errors.append(
                    f'Python class name {class_model.name} must be a valid identifier'
                )

            errors.extend(self._validate_python_attributes(class_model))

            for method in class_model.methods:
                errors.extend(
                    self._validate_python_method_identifiers(
                        owner_name=f'class {class_model.name}',
                        method=method,
                    )
                )

        for interface in graph.interfaces:
            if not self._is_python_identifier(interface.name):
                errors.append(
                    f'Python interface name {interface.name} must be a valid identifier'
                )

            for method in interface.methods:
                errors.extend(
                    self._validate_python_method_identifiers(
                        owner_name=f'interface {interface.name}',
                        method=method,
                    )
                )

        return errors

    def _validate_python_attributes(self, class_model: ClassModel) -> list[str]:
        errors: list[str] = []
        mapped_names: Counter[str] = Counter()

        for attribute in class_model.attributes:
            mapped_name = self._python_attribute_name(
                modifier=attribute.access_modifier,
                name=attribute.name,
            )

            if not self._is_python_identifier(mapped_name):
                errors.append(
                    f'Python attribute name {attribute.name} in class '
                    f'{class_model.name} must produce a valid identifier'
                )

            mapped_names[mapped_name] += 1

        for mapped_name, count in mapped_names.items():
            if count > 1:
                errors.append(
                    f'Duplicate generated Python attribute name {mapped_name} '
                    f'in class {class_model.name}'
                )

        return errors

    def _validate_python_method_identifiers(
        self,
        *,
        owner_name: str,
        method: MethodModel,
    ) -> list[str]:
        errors: list[str] = []

        if not self._is_python_identifier(method.name):
            errors.append(
                f'Python method name {method.name} in {owner_name} must be a '
                'valid identifier'
            )

        for argument in method.arguments:
            if argument.name == 'self':
                errors.append(
                    f'Python argument self in method {method.name} of {owner_name} '
                    'conflicts with generated self parameter'
                )
            elif not self._is_python_identifier(argument.name):
                errors.append(
                    f'Python argument name {argument.name} in method {method.name} '
                    f'of {owner_name} must be a valid identifier'
                )

        return errors

    def _validate_python_method_names(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for class_model in graph.classes:
            errors.extend(
                self._validate_python_owner_method_names(
                    owner_name=f'class {class_model.name}',
                    methods=class_model.methods,
                )
            )

        for interface in graph.interfaces:
            errors.extend(
                self._validate_python_owner_method_names(
                    owner_name=f'interface {interface.name}',
                    methods=interface.methods,
                )
            )

        return errors

    def _validate_python_owner_method_names(
        self,
        *,
        owner_name: str,
        methods: list[MethodModel],
    ) -> list[str]:
        errors: list[str] = []
        method_names: Counter[str] = Counter(method.name for method in methods)

        for method_name, count in method_names.items():
            if count > 1:
                errors.append(
                    f'Duplicate Python method name {method_name} in {owner_name}'
                )

        return errors

    def _validate_python_parents(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []
        analyzer = UMLGraphAnalyzer(graph)

        for class_model in graph.classes:
            parent_names: list[str] = []
            parent_class = analyzer.get_parent_class(class_model)

            if parent_class is not None:
                parent_names.append(parent_class.name)

            parent_names.extend(
                interface.name
                for interface in analyzer.get_parent_interfaces(class_model)
            )

            errors.extend(
                self._validate_python_parent_names(
                    owner_name=f'class {class_model.name}',
                    parent_names=parent_names,
                )
            )

        for interface in graph.interfaces:
            parent_names = [
                parent.name for parent in analyzer.get_parent_interfaces(interface)
            ]
            errors.extend(
                self._validate_python_parent_names(
                    owner_name=f'interface {interface.name}',
                    parent_names=parent_names,
                )
            )

        return errors

    def _validate_python_parent_names(
        self,
        *,
        owner_name: str,
        parent_names: list[str],
    ) -> list[str]:
        errors: list[str] = []
        parent_name_counts: Counter[str] = Counter(parent_names)

        for parent_name in parent_names:
            if not self._is_python_identifier(parent_name):
                errors.append(
                    f'Python parent name {parent_name} for {owner_name} must be '
                    'a valid identifier'
                )

        for parent_name, count in parent_name_counts.items():
            if count > 1:
                errors.append(f'Duplicate Python parent {parent_name} for {owner_name}')

        return errors

    def _validate_java_classes(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for class_model in graph.classes:
            if class_model.access_modifier in (
                AccessModifier.PRIVATE,
                AccessModifier.PROTECTED,
            ):
                errors.append(
                    f'Java top-level class {class_model.name} cannot be '
                    f'{class_model.access_modifier.value}'
                )

            for method in class_model.methods:
                errors.extend(self._validate_java_class_method(class_model, method))

        return errors

    def _validate_java_class_method(
        self,
        class_model: ClassModel,
        method: MethodModel,
    ) -> list[str]:
        errors: list[str] = []
        method_name = f'method {method.name} in class {class_model.name}'

        if method.is_abstract and not class_model.is_abstract:
            errors.append(
                f'Java {method_name} is abstract, but class {class_model.name} '
                'is not abstract'
            )

        if method.is_abstract and method.access_modifier == AccessModifier.PRIVATE:
            errors.append(f'Java abstract {method_name} cannot be private')

        if method.is_abstract and method.is_final:
            errors.append(f'Java abstract {method_name} cannot be final')

        if method.is_abstract and method.is_static:
            errors.append(f'Java abstract {method_name} cannot be static')

        return errors

    def _validate_java_interface_methods(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for interface in graph.interfaces:
            for method in interface.methods:
                method_name = f'method {method.name} in interface {interface.name}'

                if method.access_modifier != AccessModifier.PUBLIC:
                    errors.append(f'Java interface {method_name} must be public')

                if method.is_final:
                    errors.append(f'Java interface {method_name} cannot be final')

                if method.is_static:
                    errors.append(f'Java interface {method_name} cannot be static')

        return errors

    def _validate_java_interface_implementations(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []
        analyzer = UMLGraphAnalyzer(graph)

        for class_model in graph.classes:
            implemented_interfaces = analyzer.get_parent_interfaces(class_model)
            if not implemented_interfaces:
                continue

            class_methods = {
                self._method_signature(method): method for method in class_model.methods
            }

            for interface in implemented_interfaces:
                errors.extend(
                    self._validate_java_interface_implementation(
                        class_model=class_model,
                        interface=interface,
                        class_methods=class_methods,
                    )
                )

        return errors

    def _validate_java_interface_implementation(
        self,
        *,
        class_model: ClassModel,
        interface: InterfaceModel,
        class_methods: dict[str, MethodModel],
    ) -> list[str]:
        errors: list[str] = []

        for interface_method in interface.methods:
            signature = self._method_signature(interface_method)
            class_method = class_methods.get(signature)

            if class_method is None:
                continue

            if class_method.return_type != interface_method.return_type:
                errors.append(
                    f'Java method {class_method.name} in class {class_model.name} '
                    f'must return {interface_method.return_type} to implement '
                    f'interface {interface.name}'
                )

            if class_method.access_modifier != AccessModifier.PUBLIC:
                errors.append(
                    f'Java method {class_method.name} in class {class_model.name} '
                    f'must be public to implement interface {interface.name}'
                )

            if class_method.is_static:
                errors.append(
                    f'Java static method {class_method.name} in class '
                    f'{class_model.name} cannot implement interface {interface.name}'
                )

        return errors

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

    def _python_attribute_name(
        self,
        *,
        modifier: AccessModifier | None,
        name: str,
    ) -> str:
        if modifier == AccessModifier.PRIVATE:
            return f'__{name}'

        if modifier == AccessModifier.PROTECTED:
            return f'_{name}'

        return name

    def _is_python_identifier(self, value: str | None) -> bool:
        if self._is_blank(value):
            return False

        return value.isidentifier() and not keyword.iskeyword(value)

    def _is_blank(self, value: str | None) -> bool:
        return value is None or value.strip() == ''
