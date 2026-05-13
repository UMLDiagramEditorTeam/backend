from typing import Annotated

from fastapi import Depends

from app.services.code_generation import CodeGenerationService

CodeGenerationServiceDep = Annotated[
    CodeGenerationService,
    Depends(CodeGenerationService),
]
