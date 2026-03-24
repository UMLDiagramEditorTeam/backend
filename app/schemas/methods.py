from typing import Optional
from uuid import UUID

from app.models.enums import AccessModifier
from app.schemas.base import CommonListFilters


class MethodFilters(CommonListFilters):
    class_id: Optional[UUID] = None
    interface_id: Optional[UUID] = None
    name: Optional[str] = None
    access_modifier: Optional[AccessModifier] = None
    return_type: Optional[str] = None
