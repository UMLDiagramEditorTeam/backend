from typing import Annotated

from fastapi import Depends

from app.services.uml_graph_preloader import UMLGraphPreloaderService
from app.utils.generator_factory import GeneratorFactory

UMLGraphPreloaderServiceDep = Annotated[
    UMLGraphPreloaderService, Depends(UMLGraphPreloaderService)
]


GeneratorFactoryDep = Annotated[GeneratorFactory, Depends(GeneratorFactory)]
