from typing import Annotated

from fastapi import Depends

from app.services.code_generation_validator import CodeGenerationValidator
from app.services.uml_graph_preloader import UMLGraphPreloaderService
from app.utils.generator_factory import GeneratorFactory

UMLGraphPreloaderServiceDep = Annotated[
    UMLGraphPreloaderService, Depends(UMLGraphPreloaderService)
]


GeneratorFactoryDep = Annotated[GeneratorFactory, Depends(GeneratorFactory)]

CodeGenerationValidatorDep = Annotated[
    CodeGenerationValidator,
    Depends(CodeGenerationValidator),
]
