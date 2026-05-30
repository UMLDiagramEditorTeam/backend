from uuid import UUID

from app.core.errors import CodeGenerationValidationError
from app.dependencies.utils import (
    CodeGenerationValidatorDep,
    GeneratorFactoryDep,
    UMLGraphPreloaderServiceDep,
)
from app.services.code_generation_validator import CodeGenerationValidator
from app.services.uml_graph_preloader import UMLGraphPreloaderService
from app.utils.generator_factory import GeneratorFactory, TargetLanguage
from app.utils.uml_analyzer import UMLGraphAnalyzer


class CodeGenerationService:
    __graph_loader: UMLGraphPreloaderService
    __generator_factory: GeneratorFactory
    __validator: CodeGenerationValidator

    def __init__(
        self,
        graph_loader: UMLGraphPreloaderServiceDep,
        generator_factory: GeneratorFactoryDep,
        validator: CodeGenerationValidatorDep,
    ):
        self.__graph_loader = graph_loader
        self.__generator_factory = generator_factory
        self.__validator = validator

    async def generate(
        self,
        window_id: UUID,
        language: TargetLanguage,
    ) -> dict[str, str]:

        graph = await self.__graph_loader.load_window_graph(window_id)

        errors = self.__validator.validate(graph, language)
        if errors:
            raise CodeGenerationValidationError(errors)

        analyzer = UMLGraphAnalyzer(graph)

        generator = self.__generator_factory.get(language)

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
