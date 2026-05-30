from abc import ABC, abstractmethod
from collections.abc import Callable

from app.services.uml_graph_preloader import UMLGraph

ValidationRule = Callable[[UMLGraph], list[str]]


class BaseCodeGenerationValidator(ABC):
    @abstractmethod
    def validate(self, graph: UMLGraph) -> list[str]:
        pass

    def _collect_errors(
        self,
        graph: UMLGraph,
        *rules: ValidationRule,
    ) -> list[str]:
        errors: list[str] = []

        for rule in rules:
            errors.extend(rule(graph))

        return errors
