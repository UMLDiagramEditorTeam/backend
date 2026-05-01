from typing import Annotated

from fastapi import Depends

from app.services.code_generation import CodeGenerationService, GeneratorFactory
from app.services.uml_graph_preloader import UMLGraphPreloaderService
from app.templates.templates_env import jinja_env
from app.utils.code_generater import JavaCodeGenerator, PythonCodeGenerator

UMLGraphPreloaderServiceDep = Annotated[
    UMLGraphPreloaderService, Depends(UMLGraphPreloaderService)
]


async def get_python_generator() -> PythonCodeGenerator:
    return PythonCodeGenerator(jinja_env)


async def get_java_generator() -> JavaCodeGenerator:
    return JavaCodeGenerator(jinja_env)


JavaCodeGeneratorDep = Annotated[JavaCodeGenerator, Depends(get_java_generator)]
PythonCodeGeneratorDep = Annotated[PythonCodeGenerator, Depends(get_python_generator)]


async def get_generator_factory(
    java_generator: JavaCodeGeneratorDep,
    python_generator: PythonCodeGeneratorDep,
) -> GeneratorFactory:
    return GeneratorFactory(
        java_generator=java_generator,
        python_generator=python_generator,
    )


GeneratorFactoryDep = Annotated[GeneratorFactory, Depends(get_generator_factory)]


async def get_code_generation_service(
    uml_graph_preloader: UMLGraphPreloaderServiceDep,
    generator_factory: GeneratorFactoryDep,
) -> CodeGenerationService:
    return CodeGenerationService(uml_graph_preloader, generator_factory)


CodeGenerationServiceDep = Annotated[
    CodeGenerationService,
    Depends(get_code_generation_service),
]
