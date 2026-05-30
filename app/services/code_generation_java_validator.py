from app.models import AccessModifier, ClassModel, InterfaceModel, MethodModel
from app.services.base_code_generation_validator import BaseCodeGenerationValidator
from app.services.uml_graph_preloader import UMLGraph
from app.utils.uml_analyzer import UMLGraphAnalyzer


class JavaCodeGenerationValidator(BaseCodeGenerationValidator):
    def validate(self, graph: UMLGraph) -> list[str]:
        return self._collect_errors(
            graph,
            self._validate_classes,
            self._validate_interface_methods,
            self._validate_interface_implementations,
        )

    def _validate_classes(self, graph: UMLGraph) -> list[str]:
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
                errors.extend(self._validate_class_method(class_model, method))

        return errors

    def _validate_class_method(
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

    def _validate_interface_methods(self, graph: UMLGraph) -> list[str]:
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

    def _validate_interface_implementations(self, graph: UMLGraph) -> list[str]:
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
                    self._validate_interface_implementation(
                        class_model=class_model,
                        interface=interface,
                        class_methods=class_methods,
                    )
                )

        return errors

    def _validate_interface_implementation(
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

    def _method_signature(self, method: MethodModel) -> str:
        arguments = sorted(method.arguments, key=lambda argument: argument.order_num)
        argument_types = ','.join(argument.type for argument in arguments)
        return f'{method.name}({argument_types})'
