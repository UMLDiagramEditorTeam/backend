from typing import Annotated

from fastapi import Depends

from app.templates.templates_env import jinja_env
from app.utils.code_generator import JavaCodeGenerator, PythonCodeGenerator


async def get_python_generator() -> PythonCodeGenerator:
    return PythonCodeGenerator(jinja_env)


async def get_java_generator() -> JavaCodeGenerator:
    return JavaCodeGenerator(jinja_env)


JavaCodeGeneratorDep = Annotated[JavaCodeGenerator, Depends(get_java_generator)]
PythonCodeGeneratorDep = Annotated[PythonCodeGenerator, Depends(get_python_generator)]
