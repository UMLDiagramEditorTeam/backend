from enum import Enum
from uuid import UUID

from app.services.uml_graph_preloader import UMLGraphPreloaderService
from app.utils.code_generator import JavaCodeGenerator, PythonCodeGenerator
from app.utils.uml_analyzer import UMLGraphAnalyzer


class TargetLanguage(str, Enum):
    JAVA = 'java'
    PYTHON = 'python'


class GeneratorFactory:
    def __init__(
        self,
        java_generator: JavaCodeGenerator,
        python_generator: PythonCodeGenerator,
    ):
        self._java_generator = java_generator
        self._python_generator = python_generator

    def get(self, language: TargetLanguage):
        mapping = {
            TargetLanguage.JAVA: self._java_generator,
            TargetLanguage.PYTHON: self._python_generator,
        }

        generator = mapping.get(language)

        if generator is None:
            raise ValueError(f'Unsupported language: {language}')

        return generator


class CodeGenerationService:
    def __init__(
        self,
        graph_loader: UMLGraphPreloaderService,
        generator_factory: GeneratorFactory,
    ):
        self._graph_loader = graph_loader
        self._generator_factory = generator_factory

    async def generate(
        self,
        window_id: UUID,
        language: TargetLanguage,
    ) -> dict[str, str]:

        graph = await self._graph_loader.load_window_graph(window_id)

        analyzer = UMLGraphAnalyzer(graph)

        generator = self._generator_factory.get(language)

        files: dict[str, str] = {}

        for class_model in graph.classes:
            relations = analyzer.analyze_class(class_model)

            code = generator.generate_class(
                class_model,
                extends=relations.extends,
                implements=relations.implements,
                override=relations.implemented_methods,
            )

            filename = f'{class_model.name}.{generator.extension}'

            files[filename] = code

        for interface_model in graph.interfaces:
            relations = analyzer.analyze_interface(interface_model)

            code = generator.generate_interface(
                interface_model,
                extends=relations.extends,
            )

            filename = f'{interface_model.name}.{generator.extension}'

            files[filename] = code

        return files
