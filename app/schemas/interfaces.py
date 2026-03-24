from typing import Optional
from uuid import UUID

from app.schemas.base import CommonListFilters


class InterfaceFilters(CommonListFilters):
    window_id: Optional[UUID] = None
    tile_id: Optional[UUID] = None
    name: Optional[str] = None
