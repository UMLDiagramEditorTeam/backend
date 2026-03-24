from typing import Optional
from uuid import UUID

from app.models.enums import AccessModifier
from app.schemas.base import CommonListFilters


class ClassFilters(CommonListFilters):
    window_id: Optional[UUID] = None
    tile_id: Optional[UUID] = None
    name: Optional[str] = None
    access_modifier: Optional[AccessModifier] = None
    is_abstract: Optional[bool] = None
