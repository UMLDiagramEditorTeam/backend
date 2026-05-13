from enum import Enum

from app.dependencies.code_generators import (
    JavaCodeGeneratorDep,
    PythonCodeGeneratorDep,
)
from app.utils.code_generator import JavaCodeGenerator, PythonCodeGenerator


class TargetLanguage(str, Enum):
    JAVA = 'java'
    PYTHON = 'python'


class GeneratorFactory:
    __java_generator: JavaCodeGenerator
    __python_generator: PythonCodeGenerator

    def __init__(
        self,
        java_generator: JavaCodeGeneratorDep,
        python_generator: PythonCodeGeneratorDep,
    ):
        self.__java_generator = java_generator
        self.__python_generator = python_generator

    def get(self, language: TargetLanguage):
        mapping = {
            TargetLanguage.JAVA: self.__java_generator,
            TargetLanguage.PYTHON: self.__python_generator,
        }

        generator = mapping.get(language)

        if generator is None:
            raise ValueError(f'Unsupported language: {language}')

        return generator
