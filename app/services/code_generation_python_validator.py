import keyword
from collections import Counter

from app.models import AccessModifier, ClassModel, MethodModel
from app.services.uml_graph_preloader import UMLGraph
from app.utils.uml_analyzer import UMLGraphAnalyzer


class PythonCodeGenerationValidator:
    def validate(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        errors.extend(self._validate_identifiers(graph))
        errors.extend(self._validate_method_names(graph))
        errors.extend(self._validate_parents(graph))

        return errors

    def _validate_identifiers(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for class_model in graph.classes:
            if not self._is_python_identifier(class_model.name):
                errors.append(
                    f'Python class name {class_model.name} must be a valid identifier'
                )

            errors.extend(self._validate_attributes(class_model))

            for method in class_model.methods:
                errors.extend(
                    self._validate_method_identifiers(
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
                    self._validate_method_identifiers(
                        owner_name=f'interface {interface.name}',
                        method=method,
                    )
                )

        return errors

    def _validate_attributes(self, class_model: ClassModel) -> list[str]:
        errors: list[str] = []
        mapped_names: Counter[str] = Counter()

        for attribute in class_model.attributes:
            mapped_name = self._attribute_name(
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

    def _validate_method_identifiers(
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

    def _validate_method_names(self, graph: UMLGraph) -> list[str]:
        errors: list[str] = []

        for class_model in graph.classes:
            errors.extend(
                self._validate_owner_method_names(
                    owner_name=f'class {class_model.name}',
                    methods=class_model.methods,
                )
            )

        for interface in graph.interfaces:
            errors.extend(
                self._validate_owner_method_names(
                    owner_name=f'interface {interface.name}',
                    methods=interface.methods,
                )
            )

        return errors

    def _validate_owner_method_names(
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

    def _validate_parents(self, graph: UMLGraph) -> list[str]:
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
                self._validate_parent_names(
                    owner_name=f'class {class_model.name}',
                    parent_names=parent_names,
                )
            )

        for interface in graph.interfaces:
            parent_names = [
                parent.name for parent in analyzer.get_parent_interfaces(interface)
            ]
            errors.extend(
                self._validate_parent_names(
                    owner_name=f'interface {interface.name}',
                    parent_names=parent_names,
                )
            )

        return errors

    def _validate_parent_names(
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

    def _attribute_name(
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
        if value is None or value.strip() == '':
            return False

        return value.isidentifier() and not keyword.iskeyword(value)
