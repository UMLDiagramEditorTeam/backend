from abc import ABC, abstractmethod

from jinja2 import Environment

from app.models import AccessModifier, ClassModel, InterfaceModel


class BaseCodeGenerator(ABC):
    extension: str

    @abstractmethod
    def generate_class(
        self,
        class_model: ClassModel,
        *,
        extends: ClassModel | None,
        implements: list[InterfaceModel],
    ) -> str:
        pass

    @abstractmethod
    def generate_interface(
        self,
        interface_model: InterfaceModel,
        *,
        extends: list[InterfaceModel],
    ) -> str:
        pass


class JavaCodeGenerator(BaseCodeGenerator):
    extension = 'java'

    def __init__(self, env: Environment):
        self._env = env

    def generate_class(
        self,
        class_model: ClassModel,
        *,
        extends: ClassModel | None,
        implements: list[InterfaceModel],
    ) -> str:

        template = self._env.get_template('java/class.j2')

        return template.render(
            class_=class_model,
            extends=extends,
            implements=implements,
            modifier=self._map_modifier,
        )

    def generate_interface(
        self,
        interface_model: InterfaceModel,
        *,
        extends: list[InterfaceModel],
    ) -> str:

        template = self._env.get_template('java/interface.j2')

        return template.render(
            interface=interface_model,
            extends=extends,
            modifier=self._map_modifier,
        )

    def _map_modifier(
        self,
        modifier: AccessModifier | None,
    ) -> str:
        if modifier is None:
            return ''

        mapping = {
            AccessModifier.PUBLIC: 'public',
            AccessModifier.PRIVATE: 'private',
            AccessModifier.PROTECTED: 'protected',
            AccessModifier.DEFAULT: '',
        }

        return mapping[modifier]


class PythonCodeGenerator(BaseCodeGenerator):
    extension = 'py'

    def __init__(self, env: Environment):
        self._env = env

    def generate_class(
        self,
        class_model: ClassModel,
        *,
        extends: ClassModel | None,
        implements: list[InterfaceModel],
    ) -> str:

        template = self._env.get_template('python/class.j2')

        return template.render(
            class_=class_model,
            extends=extends,
            implements=implements,
            map_modifier=self._map_attribute_name,
            has_abstract=self._has_abstract_methods(class_model),
        )

    def generate_interface(
        self,
        interface_model: InterfaceModel,
        *,
        extends: list[InterfaceModel],
    ) -> str:

        template = self._env.get_template('python/interface.j2')

        return template.render(
            interface=interface_model,
            extends=extends,
        )

    def _map_attribute_name(
        self,
        modifier: AccessModifier | None,
        name: str,
    ) -> str:

        if modifier == AccessModifier.PRIVATE:
            return f'__{name}'

        if modifier == AccessModifier.PROTECTED:
            return f'_{name}'

        return name

    def _has_abstract_methods(
        self,
        class_model: ClassModel,
    ) -> bool:
        return class_model.is_abstract or any(
            method.is_abstract for method in class_model.methods
        )
