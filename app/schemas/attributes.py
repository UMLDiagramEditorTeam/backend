from typing import Optional
from uuid import UUID

from app.models.enums import AccessModifier
from app.schemas.base import CommonListFilters


class AttributeFilters(CommonListFilters):
    class_id: Optional[UUID] = None
    name: Optional[str] = None
    access_modifier: Optional[AccessModifier] = None
    type: Optional[str] = None
    is_final: Optional[bool] = None
    is_static: Optional[bool] = None
