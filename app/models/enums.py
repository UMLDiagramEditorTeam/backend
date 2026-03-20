from enum import Enum


class AccessModifier(str, Enum):
    PUBLIC = 'public'
    PRIVATE = 'private'
    PROTECTED = 'protected'
    DEFAULT = 'default'


class DiagramType(str, Enum):
    CLASS_DIAGRAM = 'class_diagram'
    SEQUENCE_DIAGRAM = 'sequence_diagram'


class RelationType(str, Enum):
    RELATION = 'relation'
    ONE = 'one'
    MANY = 'many'
    ONE_AND_ONLY_ONE = 'one and ONLY one'
    ZERO_OR_ONE = 'zero or one'
    ONE_OR_MANY = 'one or many'
    ZERO_OR_MANY = 'zero or many'


class EntityType(str, Enum):
    CLASS = 'class'
    INTERFACE = 'interface'
